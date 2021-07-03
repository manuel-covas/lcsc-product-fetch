# lcsc-product-fetch
Python script to scrape product details from lcsc.com's web page.\
Output is written out to a CSV file.

# Requirements
Python 3 or newer is required to run this.\
The dependencies listed in the `requirements.txt` file must also be satisfied:
- `alive-progress`
- `requests`

You can do this with `python -m pip install -r requirements.txt`

# Usage
```bash
python main.py <file | inline> <path | product_code[,product_code...]>
               |--- mode ---|  |------- path / product_codes -------|
```
## Arguments:
 - `mode`: mode to operate in, either `file` or `inline`
 - `path`: path to a file containing the product codes to fetch.
 - `product_code`: one or more product codes.

## Product code format:
In both modes, LCSC product codes should be provided as such:
```
C######,C######,C######...
```

## Modes of operation:
 - `file`:\
    In this mode the product codes in the file at `path` will
    be fetched and the output will be saved to `path + ".csv"`
 - `inline`:\
    In this mode, the product codes in the `product_codes` argument
    will be fetched and the output will be saved to `output.csv`

## Example usage:
```bash
python3 main.py inline C191386,C104604,C621
```
Console output:
```
Looking up product codes... |████████████████████████████████████████| 3/3 [100%] in 1.4s (2.13/s)
Found 2 out of 3 products.
Dropping the following product codes:
  - C621
Scraping product details from HTML... |████████████████████████████████████████| 2/2 [100%] in 1.5s (1.32/s)
Output written to output.csv
```
Output:
| LCSC Product Code  | Amount in Stock | Package | Manufacturer | Manufacturer Part Number | Product Description |
| ------------------ | --------------- | ------- | ------------ | ------------------------ | ------------------- |
| C191386            | 31120           | DIP-4   | Orient       | ORPC-817C                | TransistorOptocouplers 1 5000Vrms DIP-4 Optocouplers RoHS |
| C104604            | 89700           | 1206    | RALEC        | RTT06105JTP              | 1MΩ ±5% 1/4W ±100ppm/℃ 1206 Chip Resistor - Surface Mount RoHS |

`output.csv`:
```
LCSC Product Code,Amount in Stock,Package,Manufacturer,Manufacturer Part Number,Product Description
"C191386","31120","DIP-4","Orient","ORPC-817C","TransistorOptocouplers 1 5000Vrms DIP-4 Optocouplers RoHS"
"C104604","89700","1206","RALEC","RTT06105JTP","1MΩ ±5% 1/4W ±100ppm/℃ 1206 Chip Resistor - Surface Mount RoHS"
```