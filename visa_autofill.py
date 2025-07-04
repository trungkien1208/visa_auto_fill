import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from playwright.sync_api import (
    Locator,
    Page,
)
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import (
    sync_playwright,
    Error as PlaywrightError,
)

city_list = [
    "ShangHai,Shanghai",
    "GuangDong,Guangzhou",
    "GuangDong,Shenzhen",
    "FuJian,Xiamen",
]

arrival_flight_no = [
    "VN3542",
    "VN0502",
    "VN3544",
    "VN3550",
]

departure_flight_no = [
    "VN3543",
    "VN0503",
    "VN3545",
    "VN3531",
]

address_to_stay = [
    "Heng Sheng WanLi Square, No. 3, Shanghai Int'l Tourism Resort and Disney Land",
    "Room 2120, Floor 21 Zheng Jia Huan Shi Centre Building, No.372 Huanshi East Road, Yuexiu District, Guangzhou,China, 510000",
    "Golden Bull Plaza Tianxia International Center, Nanshan Science and Technology Park, Shenzhen",
    "Room 2120, Floor 21 Zheng Jia Huan Shi Centre Building, No.372 Huanshi East Road, Yuexiu District, Guangzhou,China, 510000",
]

declare_person = {
    "name": "TRUONG GIANG TRAVEL",
    "relationship": "AGENT",
    "phone": "0901269595",
    "address": "134 9K,  TAM DONG 23 ST, THOI TAM THON VILLAGE, HOC MON DISTRICT, HO CHI MINH CITY",
}

# Configuration constants (defaults - will be overridden by config from GUI)
PLUS_DAY_TO_DATE = 4
AUTO_NEXT = False
DATA_FILE = "application.xlsx"
EMAIL_LOGIN = "hientrang24hvisa@gmail.com"
PASSWORD_LOGIN = "@Trang126"
LOGIN_URL = "https://www.visaforchina.cn/user/login?site=SGN3_EN"
HEADLESS = False
USE_EXISTING_BROWSER = True
QUICK_FORM_URL = "https://consular.mfa.gov.cn/VISA/?visadata=eyJndWlkIjoiMTcwOTcxMjk0MDU0OTAiLCJleHBpcmVzX2luIjoiIiwidG1wX3NlY3JldCI6InZjZW50ZXJfMTcwOTcxMjk0MDU0OTBfOWEwZGE2MjZkODVmYWE5NzBjYTMzYzJlZjc"
FORM_URL = "https://consular.mfa.gov.cn/VISA/node"


# ---------------------------------------------------------------------------
# Helper functions -----------------------------------------------------------
# ---------------------------------------------------------------------------


def load_applicants(path: Path) -> pd.DataFrame:
    """Load applicant data from CSV or Excel into a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    if path.suffix.lower() in {".xls", ".xlsx"}:
        df = pd.read_excel(path, dtype=str)
    else:
        df = pd.read_csv(path)

    # Clear empty columns and rows
    df = df.dropna(axis=1, how='all')
    df = df.dropna(axis=0, how='all')
    
    # Replace empty strings, NaN and None with None
    df = df.replace(r'^\s*$', None, regex=True)  # Empty strings
    df = df.replace({pd.NA: None})  # pandas NA
    df = df.where(pd.notnull(df), None)  # NaN values

    return df


def ensure_browsers_available():
    """Ensure Playwright browsers are available, installing if necessary."""
    import os
    import subprocess
    import platform
    import urllib.request
    import tarfile
    import zipfile
    import json
    from pathlib import Path
    
    def show_browser_install_dialog():
        """Ask the user (via stdin) whether we may download Chromium.

        NOTE: We deliberately avoid any direct Qt / Cocoa calls here because
        ``ensure_browsers_available()`` often runs in a background thread when
        the GUI launches the automation.  Creating NSWindow subclasses outside
        the main thread crashes on macOS ("NSWindow should only be instantiated
        on the main thread!").  In the GUI context ``input()`` is monkey-
        patched to pop up a QMessageBox on the *main* thread using
        ``QMetaObject.invokeMethod`` – so this remains fully interactive while
        staying thread-safe.
        """
        response = input("This application needs to download a Chromium browser (~150 MB). Proceed? (Y/N): ").strip().lower()
        return response in ("y", "yes")
    
    def find_system_browsers():
        """Try to find system browsers that can be used with Playwright."""
        system = platform.system().lower()
        
        possible_browsers = []
        
        if system == "darwin":  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                Path.home() / "Applications" / "Google Chrome.app" / "Contents" / "MacOS" / "Google Chrome",
                Path.home() / "Applications" / "Chromium.app" / "Contents" / "MacOS" / "Chromium"
            ]
            for path in chrome_paths:
                if Path(path).exists():
                    possible_browsers.append(str(path))
        
        elif system == "windows":  # Windows
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
                Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe"
            ]
            for path in chrome_paths:
                if Path(path).exists():
                    possible_browsers.append(str(path))
        
        return possible_browsers
    
    def install_playwright_browsers():
        """Install Playwright browsers using the standard method."""
        print("📦 Installing Playwright browsers...")
        
        try:
            # Try different Python executables for installation
            python_executables = [
                sys.executable,
                "/usr/bin/python3",
                "/usr/local/bin/python3",
                "/opt/homebrew/bin/python3",  # Common on M1 Macs
                "python3",
                "python"
            ]
            
            success = False
            last_error = None
            
            for python_exe in python_executables:
                try:
                    # Test if this Python has playwright
                    test_result = subprocess.run(
                        [python_exe, "-c", "import playwright.sync_api"],
                        capture_output=True,
                        timeout=10
                    )
                    
                    if test_result.returncode != 0:
                        continue  # This Python doesn't have playwright
                    
                    print(f"🔍 Trying browser installation with: {python_exe}")
                    
                    # Install browsers with this Python
                    result = subprocess.run(
                        [python_exe, "-m", "playwright", "install", "chromium"],
                        capture_output=False,  # Show output to user
                        text=True,
                        check=True,
                        timeout=600  # 10 minute timeout for first install
                    )
                    
                    success = True
                    print(f"✅ Playwright browsers installed successfully using: {python_exe}")
                    return True
                    
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
                    last_error = e
                    print(f"❌ Failed to install with {python_exe}: {e}")
                    continue
            
            if not success:
                print(f"❌ All Python executables failed. Last error: {last_error}")
                return False
        
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False

    # Check if running as PyInstaller bundle
    is_bundled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    system = platform.system().lower()
    
    if is_bundled:
        # Running in a PyInstaller bundle - set browser path to system location
        if system == "darwin":  # macOS
            browser_cache = Path.home() / "Library" / "Caches" / "ms-playwright"
        elif system == "windows":  # Windows
            browser_cache = Path.home() / "AppData" / "Local" / "ms-playwright"
        else:  # Linux
            browser_cache = Path.home() / ".cache" / "ms-playwright"
        
        # Set environment variable to tell Playwright where browsers are
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_cache)
        logging.info("PyInstaller bundle: Set PLAYWRIGHT_BROWSERS_PATH to: %s", browser_cache)
    
    # First, try to use Playwright's standard browser detection
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            if os.path.exists(browser_path):
                logging.info("Playwright Chromium browser found at: %s", browser_path)
                return
            else:
                logging.warning("Playwright reports browser at %s but file doesn't exist", browser_path)
                # Clear the invalid path from environment to force re-detection
                if "PLAYWRIGHT_BROWSERS_PATH" in os.environ:
                    del os.environ["PLAYWRIGHT_BROWSERS_PATH"]
                if "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH" in os.environ:
                    del os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"]
    except Exception as e:
        logging.warning("Playwright browser not found: %s", e)
    
    # If Playwright browsers not available, try system browsers
    system_browsers = find_system_browsers()
    if system_browsers:
        logging.info(f"Found system browser(s): {system_browsers}")
        # Try to use system Chrome/Chromium if available
        for browser_path in system_browsers:
            try:
                # Test if the browser actually works
                from playwright.sync_api import sync_playwright
                with sync_playwright() as p:
                    # Set environment variable to use system browser
                    os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"] = browser_path
                    # Test launch
                    browser = p.chromium.launch(headless=True)
                    browser.close()
                    logging.info(f"Successfully using system browser: {browser_path}")
                    print(f"✅ Using system browser: {browser_path}")
                    return
            except Exception as e:
                logging.warning(f"Failed to use system browser {browser_path}: {e}")
                # Clear the failed path
                if "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH" in os.environ:
                    del os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"]
                continue
    
    # If no browsers found, try to install them
    logging.info("No suitable browsers found, attempting installation...")
    
    # Ask user permission for installation (in GUI mode)
    if is_bundled:  # Only ask in bundled mode
        if not show_browser_install_dialog():
            raise RuntimeError("Browser installation cancelled by user. The application cannot continue without a browser.")
    
    # Try Playwright's own installation method
    if install_playwright_browsers():
        return
    
    # If all installation methods failed, provide manual instructions
    arch = platform.machine().lower()
    
    if system == "darwin":  # macOS
        manual_instructions = (
            f"Browser installation failed (Architecture: {arch}). Please try one of these solutions:\n\n"
            "🔧 EASIEST SOLUTION - Install Google Chrome:\n"
            "1. Visit https://www.google.com/chrome/\n"
            "2. Download and install Google Chrome\n"
            "3. Restart this application\n\n"
            "🔧 ALTERNATIVE - Install Chromium via Homebrew:\n"
            "1. Open Terminal (Applications > Utilities > Terminal)\n"
            "2. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"\n"
            "3. Install Chromium: brew install --cask chromium\n"
            "4. Restart this application\n\n"
            "🛠️ ADVANCED - Python/Playwright Installation:\n"
            "1. Open Terminal (Applications > Utilities > Terminal)\n"
            "2. Install Python 3: brew install python3\n"
            "3. Install Playwright: pip3 install playwright\n"
            "4. Install browsers: playwright install chromium\n"
            "5. Restart this application\n\n"
            "🌐 NETWORK TROUBLESHOOTING:\n"
            "• Check your internet connection\n"
            "• Try disabling VPN or proxy\n"
            "• Check firewall settings\n"
            "• Try using a different network\n\n"
            "❓ If you need help, contact support with this error message."
        )
    elif system == "windows":  # Windows
        manual_instructions = (
            "Browser installation failed. Please try one of these manual solutions:\n\n"
            "🔧 EASIEST SOLUTION - Install Google Chrome:\n"
            "1. Visit https://www.google.com/chrome/\n"
            "2. Download and install Google Chrome\n"
            "3. Restart this application\n\n"
            "🔧 ALTERNATIVE - Install Chromium:\n"
            "1. Visit https://www.chromium.org/getting-involved/download-chromium\n"
            "2. Download Chromium for Windows\n"
            "3. Install and restart this application\n\n"
            "💻 ALTERNATIVE - Install via Command Prompt:\n"
            "1. Open Command Prompt as Administrator\n"
            "2. Install Python 3 from https://python.org\n"
            "3. Run: pip install playwright\n"
            "4. Run: playwright install chromium\n"
            "5. Restart this application\n\n"
            "🌐 NETWORK TROUBLESHOOTING:\n"
            "• Check your internet connection\n"
            "• Try disabling VPN or proxy\n"
            "• Check Windows Firewall settings\n"
            "• Try using a different network\n\n"
            "❓ If you need help, contact support with this error message."
        )
    else:  # Linux
        manual_instructions = (
            "Browser installation failed. Please try one of these manual solutions:\n\n"
            "🔧 EASIEST SOLUTION - Install Chromium:\n"
            "1. Run: sudo apt-get update\n"
            "2. Run: sudo apt-get install chromium-browser\n"
            "3. Restart this application\n\n"
            "🔧 ALTERNATIVE - Install Google Chrome:\n"
            "1. Visit https://www.google.com/chrome/\n"
            "2. Download and install Google Chrome\n"
            "3. Restart this application\n\n"
            "💻 ALTERNATIVE - Install via Python:\n"
            "1. Install Python 3: sudo apt-get install python3 python3-pip\n"
            "2. Install Playwright: pip3 install playwright\n"
            "3. Install browsers: playwright install chromium\n"
            "4. Restart this application\n\n"
            "🌐 NETWORK TROUBLESHOOTING:\n"
            "• Check your internet connection\n"
            "• Try disabling VPN or proxy\n"
            "• Check firewall settings (ufw/iptables)\n"
            "• Try using a different network\n\n"
            "❓ If you need help, contact support with this error message."
        )
    
    logging.error("All browser installation methods failed")
    raise RuntimeError(manual_instructions)


# ---------------------- Form Step Helpers ------------------------------- #


def step_personal_info(page: Page, applicant: Dict[str, Any]):
    """Step 1 – personal information."""

    data = {
        "full_name": applicant.get("full_name", ""),
        "birth_date": applicant.get("birth_date", ""),
        "country": applicant.get("country", ""),
        "province": applicant.get("province", ""),
        "city": applicant.get("province", ""),
        "marital_status": applicant.get("marital_status", ""),
        "id_number": str(applicant.get("id_number", "")),
        "passport_type": "Ordinary",
        "passport_number": str(applicant.get("passport_number", "")),
        "place_of_issue": applicant.get("place_of_issue", ""),
    }

    # 1.4A Country/region
    country = data["country"]
    country_element = page.locator("label:has-text('1.4A Country/region')").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_option(country_element, "input.el-input__inner", country, page)

    # # 1.4B Province/state
    province = data["province"]
    province_element = page.locator("label:has-text('1.4B Province/state')").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(province_element, "input.el-input__inner", province)

    # # 1.4C City
    city = data["city"]
    city_element = page.locator("label:has-text('1.4C City')").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(city_element, "input.el-input__inner", city)

    # 1.4D Marital status
    marital_status = data["marital_status"]
    marital_status_element = page.locator(
        "label:has-text('1.5A Marital status')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

    click_radio_button(marital_status_element, marital_status)

    # 1.6B ID number in the country of nationality
    id_number = data["id_number"]
    id_number_element = page.locator(
        "label:has-text('1.6B ID number in the country of nationality')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(id_number_element, "input.el-input__inner", id_number)

    # 1.6C Do you have any other nationality?
    other_nationality_element = page.locator(
        "label:has-text('1.6C Do you have any other nationality?')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    click_radio_button(other_nationality_element, "No")

    # 1.6F Do you have permanent resident status in any other country or region?
    permanent_resident_element = page.locator(
        "label:has-text('1.6F Do you have permanent resident status in any other country or region?')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    click_radio_button(permanent_resident_element, "No")

    # Have you ever had any other nationalities or resident status?
    other_nationality_element = page.locator(
        "label:has-text('Have you ever had any other nationalities or resident status?')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    click_radio_button(other_nationality_element, "No")

    # 1.7A Type of passport/travel document
    passport_type = data["passport_type"]
    passport_type_element = page.locator(
        "label:has-text('1.7A Type of passport/travel document')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    click_radio_button(passport_type_element, passport_type)

    # 1.7D Place of issue
    place_of_issue = data["place_of_issue"]
    place_of_issue_element = page.locator(
        "label:has-text('1.7D Place of issue')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(place_of_issue_element, "input.el-input__inner", place_of_issue)


def step_type_of_visa(page: Page, applicant: Dict[str, Any]):
    """Step 2 – type of visa."""
    data = {
        "visa_type": f"({applicant.get('visa_type', '')})",
        "entries": applicant.get("entries", ""),
    }

    # 2.1 The type of visa that you are applying for and the main purpose of your visit to China
    type_of_visa = data["visa_type"]
    type_of_visa_element = page.locator(
        "div.el-card:has(span.title:has-text('2.1 The type of visa that you are applying for and the main purpose of your visit to China'))"
    )
    pick_option(type_of_visa_element, "input.el-input__inner", type_of_visa, page)

    # 2.2 Service type
    service_type_element = page.locator(
        "div.el-card:has(span.title:has-text('2.2 Service type'))"
    )
    click_radio_button(service_type_element, "Normal")

    # 2.3A Visa validity of your application (months)
    visa_validity_element = page.locator(
        "label:has-text('2.3A Visa validity of your application (months)')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(visa_validity_element, "input.el-input__inner", "3")

    # 2.3B Maximum duration of stay of your application (days)
    max_duration_element = page.locator(
        "label:has-text('2.3B Maximum duration of stay of your application (days)')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(max_duration_element, "input.el-input__inner", "30")

    # 2.3C Entries of your application
    entries = data["entries"]
    entries_element = page.locator(
        "label:has-text('2.3C Entries of your application')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    click_radio_button(entries_element, entries)


def step_work_info(page: Page, applicant: Dict[str, Any]):
    """Step 3 – work information."""
    data = {
        "occupation": applicant.get("occupation", ""),
    }

    # 3.1 Current occupation

    occupation = data["occupation"]
    occupation_element = page.locator(
        "div.el-card:has(span.title:has-text('3.1 Current occupation'))"
    )
    pick_option(occupation_element, "input.el-input__inner", occupation, page)

    # 3.2 Work experience in the past five years – "Not applicable" checkbox
    work_exp_card = page.locator(
        "div.el-card:has(span.title:has-text('3.2 Work experience in the past five years'))"
    )

    # Element‑Plus renders the real <input type="checkbox"> inside the <label>.
    # Playwright's native checkbox helpers (`is_checked`, `check`) are the most
    # robust way to toggle it.  We still guard against it already being ticked.
    # First try to find the checked checkbox
    applicable_checkbox(work_exp_card, "Not applicable")
    # Fill in the "Please specify." textarea after clicking "Not applicable"
    try:
        remark_input = (
            page.locator("label:has-text('Please specify.')")
            .locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
            .locator("textarea.el-textarea__inner")
        )
        remark_input.wait_for(state="visible", timeout=5000)

        if occupation.lower() == "student":
            remark_input.fill("Student")
        else:
            remark_input.fill("Bussiness Owner")

    except PlaywrightTimeoutError:
        print(
            "Warning: Could not find 'Please specify' textarea for work experience, skipping..."
        )


def step_education_info(page: Page, applicant: Dict[str, Any]):
    """Step 4 – education information."""
    education = page.locator(
        "div.el-card:has(span.title:has-text('4.1 Highest diploma/degree'))"
    )
    applicable_checkbox(education, "Not applicable")


    # Fill in the "Please specify." textarea after clicking "Not applicable"
    remark_input = (
        page.locator("label:has-text('Please specify.')")
        .locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        .locator("textarea.el-textarea__inner")
    )
    try:
        remark_input.wait_for(state="visible", timeout=5000)
        remark_input.fill("Not mentioned")
    except PlaywrightTimeoutError:
        print(
            "Warning: Could not find 'Please specify' textarea for education, skipping..."
        )


def step_family_info(page: Page, applicant: Dict[str, Any]):
    """Step 5 – family information."""
    data = {
        "home_address": applicant.get("home_address", ""),
        "phone_number": str(applicant.get("phone_number", "")),
        "father_fullname": applicant.get("father_fullname", ""),
        "father_nationality": applicant.get("father_nationality", ""),
        "father_dob": applicant.get("father_dob", ""),
        "mother_fullname": applicant.get("mother_fullname", ""),
        "mother_nationality": applicant.get("mother_nationality", ""),
        "mother_dob": applicant.get("mother_dob", ""),
        "children_fullname": applicant.get("children_fullname", ""),
        "children_nationality": applicant.get("children_nationality", ""),
        "children_dob": applicant.get("children_dob", ""),
        "spouse_fullname": applicant.get("spouse_fullname", ""),
        "spouse_nationality": applicant.get("spouse_nationality", ""),
        "spouse_dob": applicant.get("spouse_dob", ""),
        "spouse_city": applicant.get("spouse_city", ""),
    }

    # 5.1 Current home address
    address = data["home_address"]
    address_element = page.locator(
        "label:has-text('5.1 Current home address')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(address_element, "input.el-input__inner", address)

    # 5.2 Phone number
    phone_number = data["phone_number"]
    phone_number_element = page.locator("label:has-text('5.2 Phone number')").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(phone_number_element, "input.el-input__inner", phone_number)

    # 5.3 Mobile phone number
    mobile_phone_number_element = page.locator(
        "label:has-text('5.3 Mobile phone number')"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(mobile_phone_number_element, "input.el-input__inner", phone_number)

    # 5.5A Spouse
    if data["spouse_fullname"]:
        spouse_family_name, spouse_given_name = (
            get_family_name_given_name_from_full_name(data["spouse_fullname"])
        )
        spouse_year, spouse_month, spouse_day = get_year_month_day_from_date(
            data["spouse_dob"]
        )
        # narrow the scope to the Spouse card first, then search inside it
        spouse_card = page.locator(
            "div.el-card:has(div.el-row:has-text('5.5A Spouse'))"
        ).first

        spouse_family_item = spouse_card.locator(
            "label[for='spouses.0.familyName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        spouse_given_item = spouse_card.locator(
            "label[for='spouses.0.firstName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

        # fill spouse's name
        fill_text(
            spouse_family_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            spouse_family_name,
        )
        fill_text(
            spouse_given_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            spouse_given_name,
        )

        spouse_nationality_item = spouse_card.locator(
            "label[for='spouses.0.nationalityCountry']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        pick_option(
            spouse_nationality_item,
            "input.el-input__inner",
            data["spouse_nationality"],
            page,
        )

        # fill spouse's date of birth
        spouse_dob_item = spouse_card.locator(
            "label[for='spouses.0.birthday']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        pick_date(spouse_dob_item, spouse_year, spouse_month, spouse_day, page)

        # country of birth
        spouse_country_of_birth_item = spouse_card.locator(
            "label[for='spouses.0.birthCountry']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        pick_option(
            spouse_country_of_birth_item,
            "input.el-input__inner",
            data["spouse_nationality"],
            page,
        )

        # city of birth
        spouse_city_of_birth_item = safe_locator(spouse_card, "label[for='spouses.0.birthCity']")
        if spouse_city_of_birth_item:
            spouse_city_of_birth_item.locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
            fill_text(
                spouse_city_of_birth_item, "input.el-input__inner", data["spouse_city"]
            )

        # spouse adress
        spouse_address = spouse_card.locator("label[for='spouses.0.address']").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        fill_text(spouse_address, "textarea.el-textarea__inner", data["home_address"])

    # 5.5B Father
    if data["father_fullname"]:
        father_family_name, father_given_name = (
            get_family_name_given_name_from_full_name(data["father_fullname"])
        )
        father_year, father_month, father_day = get_year_month_day_from_date(
            data["father_dob"]
        )
        # narrow the scope to the Father card first, then search inside it
        father_card = page.locator(
            "div.el-card:has(span.title:has-text('5.5B Father'))"
        ).first

        father_family_item = father_card.locator(
            "label[for='father.0.familyName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        father_given_item = father_card.locator(
            "label[for='father.0.firstName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

        # fill father's name
        fill_text(
            father_family_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            father_family_name,
        )
        fill_text(
            father_given_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            father_given_name,
        )

        father_nationality_item = father_card.locator(
            "label[for='father.0.nationalityCountry']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        # fill father's nationality
        pick_option(
            father_nationality_item,
            "input.el-input__inner",
            data["father_nationality"],
            page,
        )

        # fill father's date of birth
        # ----- robust date picker -----
        father_dob_item = father_card.locator("label[for='father.0.birthday']").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        pick_date(father_dob_item, father_year, father_month, father_day, page)

        # father in china
        father_in_china_item = father_card.locator(
            "label[for='father.0.inChinaFlag']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        click_radio_button(father_in_china_item, "No")
    else:
        father_header = page.locator(
            "div.choice-botton-header.el-row:has(span.title:has-text('5.5B Father'))"
        )
        applicable_checkbox(father_header, "Not applicable")

        # Fill in the "Please specify." textarea after clicking "Not applicable"
        remark_input = (
            page.locator("label[for='notApplyItems.father.remark']")
            .locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
            .locator("textarea.el-textarea__inner")
        )
        remark_input.fill("DESEASED")
        print("No father information provided")

    # 5.5C Mother
    if data["mother_fullname"]:
        mother_family_name, mother_given_name = (
            get_family_name_given_name_from_full_name(data["mother_fullname"])
        )
        mother_year, mother_month, mother_day = get_year_month_day_from_date(
            data["mother_dob"]
        )
        # narrow the scope to the Mother card first, then search inside it
        mother_card = page.locator(
            "div.el-card:has(span.title:has-text('5.5C Mother'))"
        ).first

        mother_family_item = mother_card.locator(
            "label[for='mother.0.familyName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

        mother_given_item = mother_card.locator(
            "label[for='mother.0.firstName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

        # fill mother's name
        fill_text(
            mother_family_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            mother_family_name,
        )
        fill_text(
            mother_given_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            mother_given_name,
        )

        mother_nationality_item = mother_card.locator(
            "label[for='mother.0.nationalityCountry']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        # fill mother's nationality
        pick_option(
            mother_nationality_item,
            "input.el-input__inner",
            data["mother_nationality"],
            page,
        )

        # fill mother's date of birth
        mother_dob_item = mother_card.locator("label[for='mother.0.birthday']").locator(
            "xpath=ancestor::div[contains(@class,'el-form-item')]"
        )
        pick_date(mother_dob_item, mother_year, mother_month, mother_day, page)

        # mother in china
        mother_in_china_item = mother_card.locator(
            "label[for='mother.0.inChinaFlag']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        click_radio_button(mother_in_china_item, "No")
    else:
        mother_header = page.locator(
            "div.choice-botton-header.el-row:has(span.title:has-text('5.5C Mother'))"
        )
        applicable_checkbox(mother_header, "Not applicable")
        # Fill in the "Please specify." textarea after clicking "Not applicable"
        remark_input = (
            page.locator("label[for='notApplyItems.mother.remark']")
            .locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
            .locator("textarea.el-textarea__inner")
        )
        remark_input.fill("DESEASED")
        print("No mother information provided")

    # 5.5D Children
    if data["children_fullname"]:
        children_family_name, children_given_name = (
            get_family_name_given_name_from_full_name(data["children_fullname"])
        )
        children_year, children_month, children_day = get_year_month_day_from_date(
            data["children_dob"]
        )
        # narrow the scope to the Children card first, then search inside it
        children_card = page.locator(
            "div.el-card:has(span.title:has-text('5.5D Children'))"
        ).first

        children_family_item = children_card.locator(
            "label[for='children.0.familyName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

        children_given_item = children_card.locator(
            "label[for='children.0.firstName']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")

        # fill children's name
        fill_text(
            children_family_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            children_family_name,
        )
        fill_text(
            children_given_item,
            "input.el-input__inner:not([readonly]):not([disabled])",
            children_given_name,
        )

        children_nationality_item = children_card.locator(
            "label[for='children.0.nationalityCountry']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        pick_option(
            children_nationality_item,
            "input.el-input__inner",
            data["children_nationality"],
            page,
        )

        # fill children's date of birth
        children_dob_item = children_card.locator(
            "label[for='children.0.birthday']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        pick_date(children_dob_item, children_year, children_month, children_day, page)

        # children in china
        children_in_china_item = children_card.locator(
            "label[for='children.0.inChinaFlag']"
        ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        click_radio_button(children_in_china_item, "No")
    else:
        children_header = page.locator(
            "div.choice-botton-header.el-row:has(span.title:has-text('5.5D Children'))"
        )
        applicable_checkbox(children_header, "Not applicable")

        print("No children information provided")

    # 5.5E Do you have any immediate relatives in China?
    immediate_relatives_in_china_item = page.locator(
        "label[for='relativeRelativeFlag']"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    click_radio_button(immediate_relatives_in_china_item, "No")


def step_information_on_your_travel(page: Page, applicant: Dict[str, Any]):
    """Step 6 – information on your travel."""
    data = {
        "date_of_arrival": applicant.get("date_of_arrival", ""),
        "travel_city": applicant.get("travel_city", ""),
        "emergency_fullname": applicant.get("emergency_fullname", ""),
        "emergency_phone": str(applicant.get("emergency_phone", "")),
        "emergency_relationship": applicant.get("emergency_relationship", ""),
    }
    emergency_family_name, emergency_given_name = (
        get_family_name_given_name_from_full_name(data["emergency_fullname"])
    )
    date_of_arrival_year, date_of_arrival_month, date_of_arrival_day = (
        get_year_month_day_from_date(data["date_of_arrival"])
    )

    travel_info = all_travel_info_base_on_city(data["travel_city"])
    departure_date = plus_day_to_date(data["date_of_arrival"], PLUS_DAY_TO_DATE)
    departure_date_year, departure_date_month, departure_date_day = (
        get_year_month_day_from_date(departure_date)
    )

    # 6.1A Date of arrival
    date_of_arrival_item = page.locator("label[for='arrivalCityDate']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_date(
        date_of_arrival_item,
        date_of_arrival_year,
        date_of_arrival_month,
        date_of_arrival_day,
        page,
    )

    # 6.1B Arrival train/ship/flight No.
    arrival_flight_no_item = page.locator("label[for='arrivalVehicleType']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )

    fill_text(
        arrival_flight_no_item,
        "input.el-input__inner",
        travel_info["arrival_flight_no"],
    )

    # 6.1C The city of your destination
    destination_city_item = page.locator("label[for='arrivalCity']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )

    pick_option(
        destination_city_item, "input.el-input__inner", travel_info["travel_city"], page
    )

    # 6.1D City to stay
    city_to_stay_item = page.locator("label[for='stayInfo.0.stayCity']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_option(
        city_to_stay_item, "input.el-input__inner", travel_info["travel_city"], page
    )

    # 6.1E Address to stay
    address_to_stay_item = page.locator("label[for='stayInfo.0.travelAddr']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(
        address_to_stay_item, "input.el-input__inner", travel_info["address_to_stay"]
    )

    # 6.1F Date of arrival
    date_of_arrival_item = page.locator("label[for='stayInfo.0.arrivalDate']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_date(
        date_of_arrival_item,
        date_of_arrival_year,
        date_of_arrival_month,
        date_of_arrival_day,
        page,
    )

    # 6.1G Date of departure
    date_of_departure_item = page.locator("label[for='stayInfo.0.leaveDate']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_date(
        date_of_departure_item,
        departure_date_year,
        departure_date_month,
        departure_date_day,
        page,
    )

    # 6.1H Date of departure
    date_of_departure_item_1 = page.locator("label[for='leaveDate']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_date(
        date_of_departure_item_1,
        departure_date_year,
        departure_date_month,
        departure_date_day,
        page,
    )

    # 6.1J Departure train/ship/flight No.
    departure_flight_no_item = page.locator("label[for='leaveVehicleType']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(
        departure_flight_no_item,
        "input.el-input__inner",
        travel_info["departure_flight_no"],
    )

    # 6.1K City of departure
    destination_city_item = page.locator("label[for='leaveCity']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    pick_option(
        destination_city_item, "input.el-input__inner", travel_info["travel_city"], page
    )

    # 6.2 Inviting person/contact or organization in China
    inviting_person_header = page.locator(
        "div.choice-botton-header.el-row:has(span.title:has-text('6.2 Inviting person/contact or organization in China'))"
    )
    inviting_person_not_applicable = inviting_person_header.locator(
        "label.el-checkbox"
    ).first
    inviting_person_not_applicable.click()

    # Fill in the "Please specify." textarea after clicking "Not applicable"
    remark_input = (
        page.locator("label[for='notApplyItems.invitation.remark']")
        .locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
        .locator("textarea.el-textarea__inner")
    )
    remark_input.fill("NONE")

    # 6.3 Emergency contact

    emergency_fullname_item = page.locator(
        "label[for='emergencyContactFamilyName']"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(emergency_fullname_item, "input.el-input__inner", emergency_family_name)

    emergency_given_name_item = page.locator(
        "label[for='emergencyContactFirstName']"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(emergency_given_name_item, "input.el-input__inner", emergency_given_name)

    emergency_phone_item = page.locator("label[for='emergencyPhoneNumber']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(emergency_phone_item, "input.el-input__inner", data["emergency_phone"])

    emergency_relationship_item = page.locator(
        "label[for='emergencyRelation']"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(
        emergency_relationship_item,
        "input.el-input__inner",
        data["emergency_relationship"],
    )

    # 6.4AWho will pay for this travel?
    who_will_pay_for_travel_item = page.locator("label[for='payForTravel']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    click_radio_button(who_will_pay_for_travel_item, "Self")

    # 6.5A Are you traveling with someone who shares the same passport with you?
    same_passport_item = page.locator("label[for='havePeersFlag']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    click_radio_button(same_passport_item, "No")


def step_information_on_previous_travel(page: Page, applicant: Dict[str, Any]):
    """Step 7 – information on previous travel."""
    # find all radio button with label "No"
    no_radio_buttons = page.locator("label.el-radio:has-text('No')")
    for i in range(no_radio_buttons.count()):
        no_radio_buttons.nth(i).click()
        # wait for 1 second
        page.wait_for_timeout(500)
        


def step_other_information(page: Page, applicant: Dict[str, Any]):
    """Step 8 – other information."""
    # find all radio button with label "No"
    no_radio_buttons = page.locator("label.el-radio:has-text('No')")
    for i in range(no_radio_buttons.count()):
        no_radio_buttons.nth(i).click()
        page.wait_for_timeout(500)


def step_declaration(page: Page, applicant: Dict[str, Any]):
    """Step 9 – declaration."""

    # select The person who fills in the application on behalf of the applicant radio button

    person_who_fills_in_the_application_on_behalf_of_the_applicant_item = page.locator(
        "label.el-radio:has-text('The person who fills in the application on behalf of the applicant')"
    )
    person_who_fills_in_the_application_on_behalf_of_the_applicant_item.click()

    # select The person who fills in the application on behalf of the applicant radio button

    # fill in the declaration person information
    # 9.2A Name
    declaration_person_name_item = page.locator("label[for='agentName']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(
        declaration_person_name_item, "input.el-input__inner", declare_person["name"]
    )

    # 9.2B Relationship with the applicant
    declaration_person_relationship_item = page.locator(
        "label[for='relationship']"
    ).locator("xpath=ancestor::div[contains(@class,'el-form-item')]")
    fill_text(
        declaration_person_relationship_item,
        "input.el-input__inner",
        declare_person["relationship"],
    )
    # 9.2C Address
    declaration_person_address_item = page.locator("label[for='agentAddr']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(
        declaration_person_address_item,
        "input.el-input__inner",
        declare_person["address"],
    )

    # 9.2D Telephone
    declaration_person_phone_item = page.locator("label[for='agentTel']").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    )
    fill_text(
        declaration_person_phone_item, "input.el-input__inner", declare_person["phone"]
    )

    # click on the radio button "I understand and agree with the above."
    i_understand_and_agree_with_the_above_item = page.locator(
        "label.el-radio:has-text('I understand and agree with the above.')"
    )
    i_understand_and_agree_with_the_above_item.click()





def step_upload_materials(page: Page, applicant: Dict[str, Any]):
    """Step 10 – upload materials."""

    page.locator("div.uploadFile:has-text('The page with photo')").locator(
        "input[type='file']"
    ).set_input_files("example_visa.jpg")


def fill_form(page: Page, applicant: Dict[str, Any], config: Dict[str, Any]):
    """
    Fill the visa application form with the applicant's data.

    This function orchestrates the multi-step form filling process by:
    1. Handling each form section sequentially
    2. Providing user checkpoints between steps
    3. Ensuring proper navigation between form pages
    4. Waiting for form submission confirmation

    Args:
        page: Playwright page object for browser automation
        applicant: Dictionary containing applicant data
    """

    # ============================================================================
    # STEP 1: Personal Information & File Upload
    # ============================================================================
    # Ask user if they want to upload file

    input("Start filling form, Please upload avatar material manually...")
    
    if AUTO_NEXT:
        upload_choice = "Y"
    else:
        upload_choice = show_prompt("Do you want to upload passport file? (Y/N): ", yes_no=True)
        print(upload_choice)

    if upload_choice == "Y":
        # find image file in image folder with name {passport_number}.jpeg
        image_folder = config.get("IMAGE_FOLDER")
        if image_folder:
            image_folder = Path(image_folder)
            image_file = find_image_file(image_folder, applicant['passport_number'])
            if image_file:
                upload_file(page, str(image_file), "passport") 
            else:
                print(f"Image file {image_file} not found")

    # Ask user if they want to fill personal info
    if AUTO_NEXT:
        personal_info_choice = "Y"
    else:
        personal_info_choice = (
            show_prompt("Do you want to fill personal information? (Y/N): ", yes_no=True)
        )
    
    if personal_info_choice == "Y":
        step_personal_info(page, applicant)

    # User checkpoint: Verify Step 1 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 1 Complete - Please verify personal information and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    # ============================================================================
    # STEP 2: Type of Visa Selection
    # ============================================================================
    # Wait for next page to load completely
    page.wait_for_selector("button:has-text('Next')", timeout=10_000)

    # Ask user if they want to fill visa type
    if AUTO_NEXT:
        visa_type_choice = "Y"
    else:
        visa_type_choice = (
            show_prompt("Do you want to fill visa type? (Y/N): ", yes_no=True)
        )
    if visa_type_choice == "Y":
        step_type_of_visa(page, applicant)

    # User checkpoint: Verify Step 2 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 2 Complete - Please verify visa type selection and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    # ============================================================================
    # STEP 3: Work Information
    # ============================================================================
    # Ask user if they want to fill work info
    if AUTO_NEXT:
        work_info_choice = "Y"
    else:
        work_info_choice = (
            show_prompt("Do you want to fill work information? (Y/N): ", yes_no=True)
        )
    if work_info_choice == "Y":
        step_work_info(page, applicant)

    # User checkpoint: Verify Step 3 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 3 Complete - Please verify work information and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    # ============================================================================
    # STEP 4: Education Information
    # ============================================================================
    # Ask user if they want to fill education info
    if AUTO_NEXT:
        education_info_choice = "Y"
    else:
        education_info_choice = (
            show_prompt("Do you want to fill education information? (Y/N): ", yes_no=True)
        )
    if education_info_choice == "Y":
        step_education_info(page, applicant)

    # User checkpoint: Verify Step 4 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 4 Complete - Please verify education information and press Enter to continue...")
    # Navigate to next step
    click_button(page, "Next")

    # Wait for next page to load completely
    page.wait_for_selector("button:has-text('Next')", timeout=10_000)

    # User checkpoint: Verify Step 4 completion

    # ============================================================================
    # STEP 5: Family Information
    # ============================================================================
    # Ask user if they want to fill family info
    if AUTO_NEXT:
        family_info_choice = "Y"
    else:
        family_info_choice = (
            show_prompt("Do you want to fill family information? (Y/N): ", yes_no=True)
        )
    if family_info_choice == "Y":
        step_family_info(page, applicant)

    # User checkpoint: Verify Step 5 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 5 Complete - Please verify family information and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    # Wait for next page to load completely
    page.wait_for_selector("button:has-text('Next')", timeout=10_000)

    # ============================================================================
    # STEP 6: Information on your travel
    # ============================================================================
    # Ask user if they want to fill travel info
    if AUTO_NEXT:
        travel_info_choice = "Y"
    else:
        travel_info_choice = (
            show_prompt("Do you want to fill travel information? (Y/N): ", yes_no=True)
        )
    if travel_info_choice == "Y":
        step_information_on_your_travel(page, applicant)

    # User checkpoint: Verify Step 6 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 6 Complete - Please verify travel information and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    page.wait_for_selector("button:has-text('Next')", timeout=10_000)
    # Wait for next page to load completely

    # ============================================================================
    # STEP 7: Information on previous travel
    # ============================================================================
    # Ask user if they want to fill previous travel info
    if AUTO_NEXT:
        previous_travel_info_choice = "Y"
    else:
        previous_travel_info_choice = (
            show_prompt("Do you want to fill previous travel information? (Y/N): ", yes_no=True)
        )
    if previous_travel_info_choice == "Y":
        step_information_on_previous_travel(page, applicant)

    # User checkpoint: Verify Step 7 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 7 Complete - Please verify previous travel information and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    page.wait_for_selector("button:has-text('Next')", timeout=10_000)

    # ============================================================================
    # STEP 8: Other information
    # ============================================================================
    # Ask user if they want to fill other info
    if AUTO_NEXT:
        other_info_choice = "Y"
    else:
        other_info_choice = (
            show_prompt("Do you want to fill other information? (Y/N): ", yes_no=True)
        )
    if other_info_choice == "Y":
        step_other_information(page, applicant)

    # User checkpoint: Verify Step 8 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 8 Complete - Please verify other information and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    page.wait_for_selector("button:has-text('Next')", timeout=10_000)

    # ============================================================================
    # STEP 9: Declaration
    # ============================================================================
    # Ask user if they want to fill declaration
    if AUTO_NEXT:
        declaration_choice = "Y"
    else:
        declaration_choice = (
            show_prompt("Do you want to fill declaration? (Y/N): ", yes_no=True)
        )
    if declaration_choice == "Y":
        step_declaration(page, applicant)

    # User checkpoint: Verify Step 9 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 9 Complete - Please verify declaration and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    page.wait_for_selector("button:has-text('Next')", timeout=10_000)


    # ============================================================================
    # STEP 10: Upload materials
    # ============================================================================
    # Ask user if they want to upload materials
    if AUTO_NEXT:
        upload_materials_choice = "Y"
    else:
        upload_materials_choice = (
            show_prompt("Do you want to upload materials? (Y/N): ", yes_no=True)
        )
    if upload_materials_choice == "Y":
        step_upload_materials(page, applicant)

    # User checkpoint: Verify Step 10 completion
    if not AUTO_NEXT:
        show_prompt("✓ Step 10 Complete - Please verify upload materials and press Enter to continue...")

    # Navigate to next step
    click_button(page, "Next")

    page.wait_for_selector("button:has-text('Next')", timeout=10_000)

    page.locator
    # ============================================================================
    # FINAL STEP: Form Submission
    # ============================================================================
    # Submit the completed application
  


def find_image_file(image_folder: Path, passport_number: str):
    extensions = [".jpeg", ".jpg", ".png"]
    for ext in extensions:
        image_file = image_folder / f"{passport_number}{ext}"
        if image_file.exists():
            return image_file
    return None


def applicable_checkbox(container, text: str = "Not applicable") -> bool:
    try:
        # Locate the checkbox label by text
        checkbox_label = container.locator(
            f"label.el-checkbox:has(span.el-checkbox__label:has-text('{text}'))"
        )

        # If it's not visible, skip it
        if not checkbox_label.is_visible():
            print("Checkbox not visible")
            return False

        # Find the checkbox input inside the label
        checkbox_input = checkbox_label.locator("input[type='checkbox']")

        # If it's already checked, do nothing
        if checkbox_input.is_checked():
            return True

        # Click the label to check it
        checkbox_label.click()
        return True

    except Exception as e:
        print(f"[Checkbox Error] {e}")
        return False


def plus_day_to_date(date: str, days: int):
    """Plus days to date."""
    date_obj = datetime.strptime(date, "%d/%m/%Y")
    new_date = date_obj + timedelta(days=days)
    return new_date.strftime("%d/%m/%Y")


def all_travel_info_base_on_city(city: str):
    index = city_list.index(city)
    return {
        "address_to_stay": address_to_stay[index],
        "arrival_flight_no": arrival_flight_no[index],
        "departure_flight_no": departure_flight_no[index],
        "travel_city": city,
    }


def pick_date(container, year: str, month: str, day: str, page: Page):
    """
    Selects YYYY / MM / DD inside the custom three-part date-picker.
    `container` is the <div class="el-form-item"> that holds the picker.
    """
    print(f"Picking date: {year} / {month} / {day}")
    # 1) Year – plain <input>
    container.locator(
        "div.select-date-picker-one input.el-input__inner:not([readonly]):not([disabled])"
    ).fill(year)

    # 2) Month – <el-select>
    pick_option(
        container.locator("div.select-date-picker-two"),
        "input.el-input__inner",
        month.lstrip("0"),  # dropdown shows 1-12, not 01-12
        page,
    )

    # 3) Day – disabled until month chosen → wait until enabled
    # Wait until the day input inside this date‑picker is enabled
    container.locator(
        "div.select-date-picker-three input.el-input__inner:not([disabled])"
    ).wait_for(state="visible", timeout=3_000)

    pick_option(
        container.locator("div.select-date-picker-three"),
        "input.el-input__inner",
        day.lstrip("0"),
        page,
    )


def click_radio_button(container, text: str):
    text = text.strip().lower()
    radios = container.locator("label.el-radio")

    for i in range(radios.count()):
        radio = radios.nth(i)
        label_text = radio.locator("span.el-radio__label").inner_text().strip().lower()
        if text in label_text:
            safe("click_radio_button", radio.click)
            return

    logging.warning("Radio option '%s' not found – skipped", text)


def click_button(page: Page, text: str):
    # Normalize input text
    target = text.strip().lower()

    # Get all visible buttons
    buttons = page.locator("button:visible")
    for i in range(buttons.count()):
        btn = buttons.nth(i)
        btn_text = btn.inner_text().strip().lower()
        if target in btn_text:
            safe(f"click_button '{text}'", btn.click)
            return

    logging.warning("Button with text '%s' not found – skipped", text)


def pick_option(container, trigger_selector: str, text: str, page):
    # Open the combobox
    safe("open combobox", container.locator(trigger_selector).click)

    # Find the visible dropdown
    dropdown = page.locator(
        ".el-select-dropdown.el-popper:not([style*='display: none'])"
    )

    # Get all visible options
    items = dropdown.locator("li.el-select-dropdown__item")

    # Normalize search text
    target = text.strip().lower()

    # Loop through each item and click the one that matches
    count = items.count()

    for i in range(count):
        item = items.nth(i)
        item_text = item.inner_text().strip().lower()
        if target in item_text:
            safe("pick_option click", item.click)
            # after click, wait for the dropdown to be closed
            safe("dropdown wait hidden", dropdown.wait_for, state="hidden", timeout=3_000)
            return

    logging.warning("[pick_option] No match found for '%s'", text)


def fill_text(container, trigger_selector: str, text: str):
    safe("fill_text", container.locator(trigger_selector).fill, text)


def upload_file(page: Page, file_path: str, text: str):
    page.locator(f"label:has-text('{text}')").locator(
        "xpath=ancestor::div[contains(@class,'el-form-item')]"
    ).locator("input[type='file']").set_input_files(file_path)

    wait_for_upload_and_confirm(page)


def upload_image(page: Page, file_path: str):
    page.locator("div.imgDetail").locator("input[type='file']").set_input_files(
        file_path
    )

    wait_for_upload_and_confirm(page)


def wait_for_upload_and_confirm(page: Page):
    """Wait for file upload to complete and click the confirm button."""
    # Wait for the confirm button to be visible and clickable
    confirm_button = page.locator(
        "button.confirm-button:has-text('Confirm the auto-filled passport details on the application form.')"
    )
    confirm_button.wait_for(state="visible", timeout=30_000)

    # Click the confirm button
    confirm_button.click()

    # Wait a moment for the action to complete
    page.wait_for_timeout(1000)


def get_family_name_given_name_from_full_name(full_name: str):
    """Get family name and given name from full name."""

    # example full name: "Nguyen Van A"
    # family name: "Nguyen"
    # given name: "Van A"
    if not full_name:
        return "", ""
    name_parts = full_name.split(" ")
    family_name = name_parts[0]

    given_name = " ".join(name_parts[1:])
    return family_name, given_name


def get_year_month_day_from_date(date: str):
    """Get year, month, and day from date."""
    day, month, year = date.split("/")
    return year, month, day


# ---------------------------------------------------------------------------
# Main automation routine ----------------------------------------------------
# ---------------------------------------------------------------------------


def login(page: Page):
    # debug log

    page.fill("input[placeholder='Enter your e-mail']", EMAIL_LOGIN)
    page.fill('input[placeholder="Enter the password"]', PASSWORD_LOGIN)


def open_form(page: Page):
    page.goto(FORM_URL)
    # debug log
    print("Form page loaded")

    page.click("button:has-text('Start filling in the form.')")


def main(config: Dict[str, Any]):
    """Run the automation.  `config` can override any module-level constants.

    Passing a dictionary allows callers (e.g. a GUI) to customise runtime
    behaviour without monkey-patching globals externally.
    """
    print(config)
    # Apply config overrides early, before we access any constant.
    if config:
        for key, value in config.items():
            globals()[key] = value
           
    df = load_applicants(Path(DATA_FILE))
    # log all data from df  
    print(df)
    logging.info("Loaded %d applicant rows from %s", len(df), DATA_FILE)

    results = []  # store status for each applicant

    # Ensure Playwright browsers are available
    try:
        ensure_browsers_available()
    except RuntimeError as e:
        print(f"❌ Browser setup failed: {e}")
        print("💡 Please try one of these solutions:")
        print("1. Install Google Chrome from https://www.google.com/chrome/")
        print("2. Run the application again and allow browser download")
        print("3. Check your internet connection")
        print("4. See BROWSER_INSTALLATION.md for detailed instructions")
        return
    
    try:
        with sync_playwright() as p:
            # Alternative browser configurations for different needs:
            # 
            # Option 1: Custom window size
            # browser = p.chromium.launch(
            #     headless=HEADLESS,
            #     args=['--window-size=1920,1080', '--window-position=0,0']
            # )
            # 
            # Option 2: Fullscreen mode
            # browser = p.chromium.launch(
            #     headless=HEADLESS,
            #     args=['--start-fullscreen']
            # )
            # 
            # Option 3: Specific size with resizable capability
            # browser = p.chromium.launch(
            #     headless=HEADLESS,
            #     args=['--window-size=1400,900', '--disable-web-security']
            # )
            
            browser = p.chromium.launch(
                headless=HEADLESS,
                args=[
                    '--start-maximized',  # Start with maximized window
                    '--disable-blink-features=AutomationControlled',  # Make it less detectable as automated
                    '--no-first-run',  # Skip first run setup
                    '--disable-default-apps',  # Disable default apps
                ]
            )
            context = browser.new_context(
                viewport=None,  # Allow viewport to be resizable
                no_viewport=True,  # Don't set any viewport constraints
                ignore_https_errors=True,  # Ignore HTTPS certificate errors if any
            )
            # Apply a 120-second default timeout to all actions in this context
            context.set_default_timeout(120_000)
            page = context.new_page()
            if USE_EXISTING_BROWSER is False:

                # Let the user log in manually first.
                logging.info("Opening login page: %s", LOGIN_URL)

                page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=120000)

                # debug log
                print("Login page loaded")

                login(page)

                # waiting user enter to continue
                show_prompt("Waiting Page loaded success & Press Enter to continue...")

                open_form(page)
                # debug log
                print("Form page loaded")
                show_prompt("Waiting Page loaded success & Press Enter to continue...")
            else:
                page.goto(QUICK_FORM_URL, wait_until="domcontentloaded", timeout=120000)
                show_prompt("Waiting Page loaded success & Press Enter to continue...")

            total_applicants = len(df)
            start_index = config.get("START_INDEX", 0)
            for row_num, applicant in enumerate(df.to_dict(orient="records")[start_index:], start=1):
                logging.info("Processing applicant %d / %d", row_num, total_applicants)
                # log current index & current data
                print(f"Current index: {row_num}")
                print("=== APPLICANT DATA ===")
                for key, value in applicant.items():
                    print(f"{key}: {value}")
                print("====================")
                print(f"Processing applicant {row_num} / {total_applicants}")
                try:
                    # Ensure we are on a fresh form for each applicant.
                    logging.info("Filling form for applicant %d", row_num)
                    print(f"Filling form for applicant {row_num}")
                    fill_form(page, applicant, config)
                    status = "SUCCESS"
                    error_msg = ""
                 
                    show_prompt("Application submitted successfully for row %d, Press Enter to continue to next applicant? (Y/N): ", yes_no=True)
                    
                    logging.info("Application submitted successfully for row %d", row_num)
                except PlaywrightTimeoutError:
                    status = "FAILURE"
                    error_msg = "Timeout waiting for success confirmation"
                    logging.error(error_msg)
                    show_prompt("Press Enter to continue to next applicant...")
                except Exception as exc:
                    status = "FAILURE"
                    error_msg = str(exc)
                    logging.exception("Unexpected error while submitting row %d", row_num)
                    show_prompt("Press Enter to continue to next applicant...")

                # Record the result
                results.append({**applicant, "status": status, "error": error_msg})

            # End of iteration.
            browser.close()
    except Exception as e:
        print(f"❌ Failed to launch browser: {e}")
        print("💡 This usually means:")
        print("   - No browser is installed")
        print("   - Browser installation is incomplete")
        print("   - System permissions issues")
        print("   - Try running the application again")
        print("\n🔧 Quick fixes to try:")
        print("   1. Install Google Chrome from https://www.google.com/chrome/")
        print("   2. Run the application again and allow browser download when prompted")
        print("   3. Check your internet connection")
        print("   4. See BROWSER_INSTALLATION.md for detailed instructions")
        
        # For end users, provide more specific guidance
        if getattr(sys, 'frozen', False):
            print("\n📋 FOR END USERS:")
            print("   This is a common issue when running the app for the first time.")
            print("   The app needs to download a browser (~150 MB) to work.")
            print("\n   🔧 SIMPLE SOLUTION:")
            print("   1. Close this application")
            print("   2. Make sure you have internet connection")
            print("   3. Run the application again")
            print("   4. When prompted, click 'Yes' to allow browser download")
            print("\n   🔧 ALTERNATIVE SOLUTION:")
            print("   1. Install Google Chrome from https://www.google.com/chrome/")
            print("   2. Restart this application")
            print("\n   📞 Need help? Contact support with this error message.")
        
        return



# ---------------------------------------------------------------------------
# Default runtime constants (can be overridden via `main(config)`)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Safe wrapper --------------------------------------------------------------
# ---------------------------------------------------------------------------


def safe(desc: str, fn, *args, **kwargs):
    """Execute *fn* ignoring Playwright locator errors.

    Any *PlaywrightTimeoutError*, generic *PlaywrightError*, or *ValueError* is
    logged and suppressed so the automation can continue.
    """

    try:
        return fn(*args, **kwargs)
    except (PlaywrightTimeoutError, PlaywrightError, ValueError) as exc:
        logging.warning("SAFE-IGNORED: %s → %s", desc, exc)
        return None

def safe_locator(container, locator: str) -> Locator | None:
    try:
        return container.locator(locator)
    except Exception as exc:
        logging.warning("SAFE-IGNORED: %s → %s", locator, exc)
        return None


def show_prompt(prompt: str, yes_no: bool = False):
    print(prompt)
    if yes_no:
        data_input = input(f"{prompt}(Y/N): ")
        
        return data_input.upper()
    else:
        data_input = input(f"{prompt}")
        
        return data_input.upper()