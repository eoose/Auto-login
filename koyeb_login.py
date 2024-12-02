import os
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def should_run_today(last_login_file, max_interval_days=15):
    """
    确定今天是否应该运行登录任务：
    1. 如果最近运行日期不存在或无效，返回 True。
    2. 如果上次运行超过 max_interval_days 天，返回 True。
    3. 在 1 到 max_interval_days 内随机选择一天运行。
    """
    today = datetime.now().date()

    try:
        with open(last_login_file, 'r') as f:
            content = f.read().strip()
            if not content:
                raise ValueError("File is empty")
            last_login_date = datetime.strptime(content, "%Y-%m-%d").date()
    except (FileNotFoundError, ValueError) as e:
        # 文件不存在或内容无效时，立即运行
        print(f"Could not read last login date ({e}). Running task today.")
        return True

    days_since_last_run = (today - last_login_date).days

    if days_since_last_run > max_interval_days:
        print(f"Last login was {days_since_last_run} days ago. Running task today.")
        return True  # 超过最大间隔，必须运行
    if days_since_last_run == 0:
        print("Task already ran today. Skipping.")
        return False  # 同一天避免重复运行

    # 随机决定今天是否运行
    decision = random.choice([True, False])
    print(f"Last login was {days_since_last_run} days ago. Random decision to run: {decision}")
    return decision

def login_koyeb(email, password):
    url = "https://app.koyeb.com/auth/signin"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # 打开 Koyeb 登录页面
            page.goto(url)

            # 填写邮箱和密码
            page.fill('input[name="email"]', email)
            page.fill('input[name="password"]', password)

            # 点击登录按钮
            page.click('button[type="submit"]')

            # 等待登录成功
            try:
                # 调整等待时间和选择器
                page.wait_for_selector("text=Dashboard", timeout=20000)  
                print("Login successful, page title:", page.title())
            except Exception as e:
                # 打印页面状态以帮助调试
                print("Login failed. Page content:")
                print(page.content())  # 输出页面 HTML 内容
                raise e  # 抛出原始异常

    except Exception as e:
        print(f"An error occurred during login: {e}")
    finally:
        if 'browser' in locals():
            browser.close()

if __name__ == "__main__":
    last_login_file = "last_login_date.txt"
    max_interval_days = 15

    # 检查是否需要运行任务
    if should_run_today(last_login_file, max_interval_days):
        email = os.getenv("KOYEB_EMAIL")
        password = os.getenv("KOYEB_PASSWORD")

        if not email or not password:
            raise ValueError("KOYEB_EMAIL 和 KOYEB_PASSWORD 环境变量未设置")

        # 执行登录
        login_koyeb(email, password)

        # 记录登录的日期
        today = datetime.now().date()
        with open(last_login_file, 'w') as f:
            f.write(str(today))
        print(f"Task completed. Last login date updated to {today}.")
    else:
        print("Skipping login today.")
