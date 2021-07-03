import sys
import asyncio
import time
import requests
import json
from alive_progress import alive_bar

def print_usage():
    print("Usage:\n")
    print("  {} <file | inline> <path | product_code[,product_code...]>".format(sys.argv[0]))
    print("\nArguments:\n")
    print("  mode: mode to operate in, either 'file' or 'inline'")
    print("  path: path to a file containing the product codes to fetch.")
    print("  product_code: one or more product codes.")
    print("\nProduct code format:\n")
    print("  In both modes, LCSC product codes should be provided as such:")
    print("    C######,C######,C######...")
    print("\nModes of operation:\n")
    print("  'file':")
    print("    In this mode the product codes in the file at 'path' will")
    print("    be fetched and the output will be saved to <path>'.csv'\n")
    print("  'inline':")
    print("    In this mode, the product codes in the 'product_code' argument")
    print("    will be fetched and the output will be saved to 'output.csv'\n")
    exit()

if len(sys.argv) < 3:
    print("Missing arguments.\n")
    print_usage()


# Parse arguments

opertion_mode = sys.argv[1]
product_codes = []

if opertion_mode == "file":
    product_codes = open(sys.argv[2], "r").read().split(",")

elif opertion_mode == "inline":
    product_codes = sys.argv[2].split(",")

else:
    print("Invalid mode '{}'\n".format(opertion_mode))
    print_usage()


# Looks up a product code.

def lookup_product_code(product_code, progress_bar):
    try:
        response = json.loads(requests.get("https://lcsc.com/api/global/additional/search?q={}".format(product_code)).text)

        if response["success"]:
            if response["result"]["lcsc_part_number"]:
                progress_bar()
                return {
                    "success": True, 
                    "product_code": product_code,
                    "url": "https://lcsc.com"+response["result"]["links"]
                }
    except:
        pass
    progress_bar()
    return {
        "success": False,
        "product_code": product_code
    }


# Asynchronous product lookup

async def lookup_product_codes():

    event_loop = asyncio.get_running_loop()
    co_routines = []
    valid_products = []
    dropped_products = []

    # Proceed to looking up loaded product codes.
    with alive_bar(len(product_codes), "Looking up product codes...") as progress_bar:

        # Start asynchronous lookups
        for product_code in product_codes:
            co_routines.append(event_loop.run_in_executor(None, lookup_product_code, product_code, progress_bar))
            time.sleep(.1)

        # Process results
        for co_routine in co_routines:
            result = await co_routine

            if result["success"]:
                valid_products.append(result)
            else:
                dropped_products.append(result)

    return {
        "valid_products": valid_products,
        "dropped_products": dropped_products
    }


# Lookup product codes

lookup_result = asyncio.run(lookup_product_codes())
valid_products = lookup_result["valid_products"]
dropped_products = lookup_result["dropped_products"]

if len(valid_products) == 0:
    print("No products were found.")
    exit()

print("Found {} out of {} products.".format(len(valid_products), len(product_codes)))
print("Dropping the following product codes:")

for product in dropped_products:
    print("  - {}".format(product["product_code"]))



# Scrapes a product's details from HTML

def scrape_product_details(product, progress_bar):
    
    try:
        response = requests.get(product["url"]).text
        scraped_product = {
            "manufacturer":             response.split('<td> Manufacturer </td>')[1].split('class="detail-brand-title">')[1].split('</a>')[0],
            "manufacturer_part_number": response.split('<td>Mfr.Part #</td>')[1].split('<td class="detail-mpn-title">')[1].split('</td>')[0],
            "lcsc_product_code":        response.split('<td>LCSC Part #</td>')[1].split('<td id="product-id" data-id="')[1].split('">')[1].split('</td>')[0],
            "package":                  response.split('<td>Package</td>')[1].split('<td>')[1].split('</td>')[0],
            "product_description":      response.split('Description</td>')[1].split('<td><p>')[1].split('</p></td>')[0],
            "amount_in_stock":          response.split('<span class="all-stock">')[1].split('</span>')[0]
        }
        progress_bar()
        return scraped_product
    except Exception as err:
        pass

    progress_bar()
    return None


# Asynchronous product scrape

async def scrape_products():

    event_loop = asyncio.get_running_loop()
    co_routines = []
    scraped_data = {
        "manufacturer": [],
        "manufacturer_part_number": [],
        "lcsc_product_code": [],
        "package": [],
        "product_description": [],
        "amount_in_stock": []
    }

    # Proceed to scrape product details.
    with alive_bar(len(valid_products), "Scraping product details from HTML...") as progress_bar:

        # Start asynchronous lookups
        for product in valid_products:
            co_routines.append(event_loop.run_in_executor(None, scrape_product_details, product, progress_bar))
            time.sleep(.1)

        # Process results
        for co_routine in co_routines:

            scraped_product = await co_routine
            if scraped_product == None:
                continue

            scraped_data["manufacturer"].append(scraped_product["manufacturer"])
            scraped_data["manufacturer_part_number"].append(scraped_product["manufacturer_part_number"])
            scraped_data["lcsc_product_code"].append(scraped_product["lcsc_product_code"])
            scraped_data["package"].append(scraped_product["package"])
            scraped_data["product_description"].append(scraped_product["product_description"])
            scraped_data["amount_in_stock"].append(scraped_product["amount_in_stock"])
    
    return scraped_data


scraped_data = asyncio.run(scrape_products())
output_csv = "LCSC Product Code,Amount in Stock,Package,Manufacturer,Manufacturer Part Number,Product Description"

for i in range(len(scraped_data["lcsc_product_code"])):

    output_csv += '\n"{}","{}","{}","{}","{}","{}"'.format(
        scraped_data["lcsc_product_code"][i],
        scraped_data["amount_in_stock"][i],
        scraped_data["package"][i],
        scraped_data["manufacturer"][i],
        scraped_data["manufacturer_part_number"][i],
        scraped_data["product_description"][i]
    )

if opertion_mode == "file":
    open(sys.argv[2]+".csv", "w").write(output_csv)
    print("Output written to "+sys.argv[2]+".csv")
elif opertion_mode == "inline":
    open("output.csv", "w").write(output_csv)
    print("Output written to output.csv")