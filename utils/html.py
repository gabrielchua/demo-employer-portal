from bs4 import BeautifulSoup
import json
import re

def color_table_headers(html_string, bg_color="white", font_color="black"):
    soup = BeautifulSoup(html_string, "html.parser")

    # Find the row in the table header (thead)
    header_row = soup.find("thead").find("tr")
    if header_row:
        header_row["style"] = f"background-color: {bg_color}; color: {font_color};"

    # Center align the text for all cells in the table
    for cell in soup.find_all(["td", "th"]):
        current_style = cell.get("style", "")
        cell["style"] = f"{current_style}; text-align: center; vertical-align: middle;"

    # Embed the CSS for center alignment directly into the HTML
    css_string = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: center;
            vertical-align: middle;
            border: 1px solid black;
            padding: 8px;
        }
    </style>
    """

    # Ensure there is a <head> element to append the CSS
    if soup.head:
        soup.head.append(BeautifulSoup(css_string, "html.parser"))
    else:
        head = soup.new_tag("head")
        soup.insert(0, head)
        head.append(BeautifulSoup(css_string, "html.parser"))

    return str(soup)

def clean_html(text):
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    
    # Replace HTML escape entities with their characters
    cleantext = cleantext.replace('&amp;', '&')
    cleantext = cleantext.replace('&lt;', '<')
    cleantext = cleantext.replace('&gt;', '>')
    cleantext = cleantext.replace('&quot;', '"')
    cleantext = cleantext.replace('&#39;', "'")
    
    # Remove line breaks
    cleantext = cleantext.replace('\n', ' ')  # Replace with space. If you prefer no space, replace with ''
    
    # Remove full HTTP links
    cleantext = re.sub(r'http\S+', '', cleantext)
    
    return cleantext

def get_mcf_job(mcf_url, http):
    regex_matches = re.search('\\-{1}([a-z0-9]{32})\\?', mcf_url + "?")
    mcf_uuid = regex_matches.group(1)
    resp = http.request('GET',f'https://api.mycareersfuture.gov.sg/v2/jobs/{mcf_uuid}')
    return json.loads(resp.data)
