import os
from datetime import datetime
from playwright.sync_api import sync_playwright

def login_koyeb(email, password):
    url = "https://app.koyeb.com/auth/signin"
    last_run_file = os.path.join(os.getcwd(), "last_login_date.txt")

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

        # 等待页面跳转
        page.wait_for_timeout(5000)
        print(f"Current URL: {page.url}")
        if page.url == "https://app.koyeb.com/":
            print(f"Login successful for account: {email}")
            
            # 更新登录日期到文件
            today = datetime.now().date()
            try:
                with open(last_run_file, "w") as f:
                    f.write(str(today))
                print(f"File updated successfully at {last_run_file}.")
            except Exception as e:
                print(f"Error updating {last_run_file}: {e}")
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
