import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def login_koyeb(email, password):
    url = "https://app.koyeb.com/auth/signin"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 打开登录页面
        page.goto(url)

        # 填写邮箱和密码
        page.fill('input[name="email"]', email)
        page.fill('input[name="password"]', password)

        # 点击登录按钮
        page.click('button[type="submit"]')

        # 等待跳转
        page.wait_for_url("https://app.koyeb.com/", timeout=30000)

        # 检查登录是否成功
        if page.url == "https://app.koyeb.com/":
            print(f"Login successful for account: {email}")
        else:
            raise Exception("Login failed. Please check your credentials.")

        browser.close()

if __name__ == "__main__":
    email = os.getenv("KOYEB_EMAIL")
    password = os.getenv("KOYEB_PASSWORD")

    if not email or not password:
        raise ValueError("Environment variables KOYEB_EMAIL and KOYEB_PASSWORD must be set.")

    # 尝试登录
    try:
        login_koyeb(email, password)

        # 更新登录日期
        today = datetime.now().date()
        with open("last_login_date.txt", "w") as f:
            f.write(str(today))
        print("File updated successfully: last_login_date.txt")
    except Exception as e:
        print(f"An error occurred: {e}")
