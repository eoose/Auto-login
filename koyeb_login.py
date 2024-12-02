import os
import random
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

def should_run_today(last_run_file, max_interval_days=15):
    """
    确定今天是否应该运行登录任务：
    1. 如果最近运行日期不存在，返回 True。
    2. 如果上次运行超过 max_interval_days 天，返回 True。
    3. 在 1 到 max_interval_days 内随机选择一天运行。
    """
    today = datetime.now().date()

    try:
        with open(last_run_file, 'r') as f:
            last_run_date = datetime.strptime(f.read().strip(), "%Y-%m-%d").date()
    except FileNotFoundError:
        # 没有记录时，立即运行
        return True

    days_since_last_run = (today - last_run_date).days

    if days_since_last_run > max_interval_days:
        return True  # 超过最大间隔，必须运行
    if days_since_last_run == 0:
        return False  # 同一天避免重复运行

    # 随机决定今天是否运行
    return random.choice([True, False])

def login_koyeb(email, password):
    url = "https://app.koyeb.com/auth/signin"

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

        # 等待页面跳转，直到 URL 变为目标 URL
        page.wait_for_url("https://app.koyeb.com/", timeout=20000)

        # 检查当前页面 URL 是否是成功登录后的 URL
        if page.url() == "https://app.koyeb.com/":
            print("Login successful, page title:", page.title())  # 登录成功
        else:
            print("Login failed, current URL:", page.url())  # 登录失败

        # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    last_run_file = "last_run_date.txt"
    max_interval_days = 15

    if should_run_today(last_run_file, max_interval_days):
        email = os.getenv("KOYEB_EMAIL")
        password = os.getenv("KOYEB_PASSWORD")

        if not email or not password:
            raise ValueError("KOYEB_EMAIL 和 KOYEB_PASSWORD 环境变量未设置")

        login_koyeb(email, password)

        # 记录今天的日期
        today = datetime.now().date()
        with open(last_run_file, 'w') as f:
            f.write(str(today))
    else:
        print("Skipping login today.")
