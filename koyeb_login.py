import os
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def should_run_today(last_login_file, max_interval_days=15):
    """
    确定今天是否应该运行登录任务：
    1. 如果最近运行日期不存在，返回 True。
    2. 如果上次运行超过 max_interval_days 天，返回 True。
    3. 在 1 到 max_interval_days 内随机选择一天运行。
    """
    today = datetime.now().date()

    try:
        with open(last_login_file, 'r') as f:
            last_login_date = datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        # 没有记录时，立即运行
        print("No previous login record found. Running task today.")
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

            # 等待页面加载完成
            page.wait_for_selector("text=Dashboard", timeout=10000)  # 等待登录成功
            print("Login successful. Page title:", page.title())

    except Exception as e:
        print(f"An error occurred during login: {e}")
        raise
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
