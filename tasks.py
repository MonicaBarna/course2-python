from robocorp.tasks import task
from robocorp import browser, http
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.Assistant import Assistant

url = "https://robotsparebinindustries.com/#/robot-order"

@task
def order_robots_from_RobotSpareBin():
    browser.configure(
        slowmo=100,
    )
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website(url)
    # user_input_task()
    for row in get_orders():
        fill_the_form(row)
    archive_receipts()

def user_input_task():
    assistant = Assistant()
    assistant.add_heading("Input from user")
    assistant.add_text_input("text_input", placeholder="Please enter URL")
    assistant.add_submit_buttons("Submit", default="Submit")
    result = assistant.run_dialog()
    if(result.__contains__('text_input')):
        url = result.text_input
    open_robot_order_website(url)


def open_robot_order_website(url):
    browser.goto(url)

def get_orders():
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

    library = Tables()
    return library.read_table_from_csv(
        "orders.csv", header=True, columns=["Order number", "Head", "Body", "Legs", "Address"]
    )

def fill_the_form(row):
    page = browser.page()
    close_annoying_modal()

    body = row['Body']
    page.select_option("#head", row['Head'])
    page.fill(".form-control", row['Legs'])
    page.click(f"#id-body-{body}")
    page.fill("#address", row['Address'])
    page.click("#order")
    
    while(page.is_visible(".alert-danger")):
        page.click("#order")

    page = browser.page()
    document = store_receipt_as_pdf(row["Order number"])
    image = screenshot_robot(row["Order number"])
    embed_screenshot_to_receipt(document, image) 
    page.click("#order-another")

def close_annoying_modal():
    page = browser.page()
    page.wait_for_selector
    page.click("text=Yep")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    order_receipt = page.locator("#receipt").inner_html()
    document = f"output/receipts/receipt_{order_number}.pdf"

    pdf = PDF()
    pdf.html_to_pdf(order_receipt, document)
    return document

def screenshot_robot(order_number):
    page = browser.page()
    image = f"output/receipts/robot_{order_number}.png"
    page.screenshot(path=image)
    return image  

def embed_screenshot_to_receipt(pdf_file, screenshot,):
    pdf = PDF()
    list_of_files = [screenshot]
   
    pdf.add_files_to_pdf(
        files=list_of_files,
        target_document=pdf_file,
        append = True,
    )

def archive_receipts():   
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "output/receipts.zip")

