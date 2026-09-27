from robocorp.tasks import task
from robocorp import browser, vault
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

browser.configure(headless=False)

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    page = open_robot_order_website()

    close_annoying_modal(page)

    orders = get_orders()

    for order in orders:
        fill_the_form(page, order)
        preview_robot(page)
        submit_order(page)

        receipt_pdf = store_order_receipt_as_pdf(order["Order number"]
        )
        robot_screenshot = screenshot_robot(
            order["Order number"]
        )
        embed_screenshot_to_receipt(
            robot_screenshot,
            receipt_pdf
        )

        order_another_robot(page)

    
    archive_receipts()

def open_robot_order_website():
    """Avaa RobotSpareBin verkkosivun"""
    page = browser.goto(
        "https://robotsparebinindustries.com/#/robot-order"
    )
    return page


def get_orders():
    """Lataa CSV tiedoston ja palauttaa sen taulukkona."""
    http = HTTP()
    tables = Tables()
    
    
    http.download(
        url="https://robotsparebinindustries.com/orders.csv",
        target_file="orders.csv",
        overwrite=True
    )

    orders = tables.read_table_from_csv(
    "orders.csv",
    header=True
    )
    return orders

def close_annoying_modal(page):
    """ Sulkeee sivun popupin, joka estää robotin tilaamisen """
    page.click("button.btn.btn-dark")


def fill_the_form(page, order):
    """Täyttää tilauslomakkeen ja lähettää sen"""


    """Valitsee head valiksta csv mukaisen pään"""
    page.select_option("#head", index=int(order["Head"]))


    """Valitsee body valiksta csv mukaisen rungon"""
    page.set_checked(
        f"#id-body-{order['Body']}",
        True
    )
    """Täyttää legs valikosta csv mukaisen jalkojen määrän"""
    page.fill(
    "input[placeholder='Enter the part number for the legs']",
    str(order["Legs"])
)

    """Täyttää osoitekentän csv mukaisella osoitteella"""
    page.fill(
        "#address",
        str(order["Address"])
    )

def preview_robot(page):
    page.click("button.btn.btn-secondary")


def submit_order(page):
    """Yrittää uudestaan kunnes lähettää tilauksen"""
    page.click("#order")

    """Tarkistaa näkyykö virheilmoitus"""
    error_message = page.locator(".alert-danger")

    while page.locator(".alert-danger").is_visible():
        page.click("#order")

def order_another_robot(page):
    page.click("#order-another")
    close_annoying_modal(page)

def store_order_receipt_as_pdf(order_number):
    """Tallentaa tilausvahvistuksen PDF tiedostona"""
    
    page = browser.page()
    pdf = PDF()

    receipt_html = page.locator("#receipt").inner_html()

    pdf_path = f"output/receipt_{order_number}.pdf"
    pdf.html_to_pdf(
        receipt_html,
        pdf_path
    )

    return pdf_path

def screenshot_robot(order_number):
    """Tallentaa screenshotin robotista"""

    page = browser.page()

    screenshot_path = f"output/robot_{order_number}.png"

    page.locator("#robot-preview-image").screenshot(
        path=screenshot_path
        )
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Lisää robotin screenshotin kuitin PDF-tiedoston loppuun."""

    pdf = PDF()

    pdf.add_files_to_pdf(
        files=[screenshot],
        target_document=pdf_file,
        append=True
    )

def archive_receipts():
    """Pakkaa output-kansion PDF-kuitit ZIP-tiedostoksi."""

    archive = Archive()

    archive.archive_folder_with_zip(
        folder="output",
        archive_name="output/receipts.zip",
        include="*.pdf"
    )