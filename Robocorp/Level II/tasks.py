import os
from zipfile import ZipFile

from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.FileSystem import FileSystem

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    orders = get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        receipt = store_receipt_as_pdf(row['Order number'])
        screenshot = screenshot_robot(row['Order number'])
        embed_screenshot_to_receipt(screenshot, receipt)
    archive_receipts()
    
def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def get_orders():
    # Download do arquivo 
    http = HTTP()
    output_path = r"output\orders.csv"
    http.download(url="https://robotsparebinindustries.com/orders.csv",target_file=output_path, overwrite=True)
    # Le arquivo
    table = Tables()
    orders = table.read_table_from_csv(output_path)
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")
    
def fill_the_form(robot_itens):
    page = browser.page()
    page.select_option("#head",str(robot_itens["Head"]))
    page.click(f"#id-body-{str(robot_itens['Body'])}")
    page.fill("input[placeholder='Enter the part number for the legs']", str(robot_itens["Legs"]))
    page.fill("#address",robot_itens["Address"])
    page.click("#preview")
    page.click("#order")    
    while page.is_visible("#order"):
        page.click("#order")
    
def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt, f"output/order-{order_number}.pdf")
    return f"output/order-{order_number}.pdf"
    
def screenshot_robot(order_number):
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path=f"output/order-{order_number}.png")
    page.click("#order-another")
    return f"output/order-{order_number}.png"
    

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
    image_path=screenshot,
    source_path=pdf_file,
    output_path=pdf_file)
    os.remove(screenshot)
    
def archive_receipts(): 
    with ZipFile("output\orders_pdf.zip", 'w') as zipf:
        for root, dirs, files in os.walk("output"):
            for file in files:
                if file.endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    zipf.write(pdf_path, os.path.relpath(pdf_path, "output"))
                    os.remove(pdf_path)        