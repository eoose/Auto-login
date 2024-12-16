import os
from datetime import datetime
from playwright.sync_api import sync_playwright

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

        # 等待页面跳转并判断是否成功
        page.wait_for_timeout(5000)  # 等待页面加载
        if page.url == "https://app.koyeb.com/":
            print(f"Login successful for account: {email}")
            
            # 更新登录日期到文件
            today = datetime.now().date()
            with open("./last_login_date.txt", "w") as f:
                f.write(str(today))
        else:
            print("Login failed: URL did not match the expected page.")

        # 关闭浏览器
        browser.close()

if __name__ == "__main__":
    email = os.getenv("KOYEB_EMAIL")
    password = os.getenv("KOYEB_PASSWORD")

    if not email or not password:
        raise ValueError("KOYEB_EMAIL 和 KOYEB_PASSWORD 环境变量未设置")

    login_koyeb(email, password)
