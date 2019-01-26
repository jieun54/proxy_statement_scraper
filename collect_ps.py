from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
import os


def main():
    # Read an excel file that contains ticker symbols and CIK numbers of companies.
    f = open("S&P_sample.csv")
    reader = csv.reader(f)
    keys = list(reader)
    f.close()

    # Create a folder to store proxy statements.
    os.mkdir(os.path.dirname(os.path.abspath(__file__)) + '\data')

    # Extract text from each proxy statement.
    for i in range(0, len(keys)):
        try:
            table = get_doc_links(keys[i][1])
        except AttributeError:
            print("No tag found")

        for j in range(0, len(table)):
            url = table[j][3]
            html = urlopen(url)
            bs_obj = BeautifulSoup(html.read(), "lxml")
            result = bs_obj.getText()
            make_text_files(keys[i], table[j][1], result)


def make_text_files(keys, filing_date, text):
    """This function puts text files of proxy statements into a folder.
    Args:
        keys: A list that contains a ticker symbol and CIK number of a company
        filing_date: A string of filing date of a statement
        text: A long text extracted from a statement
    """
    path = os.path.dirname(os.path.abspath(__file__)) + '\data\\' + str(keys[0]) + ' ' + str(keys[1]) + ' ' + str(filing_date) + '.txt'
    print(path)
    fw = open(path, 'w', encoding='utf-8')
    fw.write(text)
    fw.close()


def parse_rows(rows):
    """This function converts a table in a html file into a list.
    Args:
        rows: A list that contains a table in html style
    Returns:
        result: A list of parsed elements
    """
    result = []
    for row in rows:
        table_dt = row.find_all('td')
        if table_dt:
            result.append([data.get_text() for data in table_dt])
    return result


def get_doc_links(cik_num):
    """This function extracts links to all proxy statements of a company.
    Args:
        cik_num: A string of CIK number of a company
    Returns:
        table_info: A list that contains lists of links that are connected to proxy statements
    """
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + cik_num + "&type=DEF+14A&dateb=&owner=exclude&count=100"
    html = urlopen(url)
    bs_obj = BeautifulSoup(html.read(), "html.parser")

    # Extract filing dates and links of documents.
    table_info = bs_obj.find("table", {"class": "tableFile2"})
    rows = table_info.findAll('tr')
    table_info = parse_rows(rows)

    # Remove unnecessary rows.
    for i in table_info:
        del(i[1:3])
        del(i[-1])

    # Extract links of documents.
    links = bs_obj.findAll("a", {'id': "documentsbutton"})
    for i in range(0, len(links)):
        partial_link = links[i].get('href')
        full_link = "https://www.sec.gov" + partial_link
        table_info[i].append(full_link)

    # Get text files from links.
    for i in range(0, len(table_info)):
        html2 = urlopen(table_info[i][2])
        bs_obj2 = BeautifulSoup(html2.read(), "html.parser")
        for link in bs_obj2.select('table.tableFile a[href]'):
            partial_link = link['href']
            # First, find a htm file.
            if "htm" in partial_link:
                table_info[i].append("https://www.sec.gov" + partial_link)
            # If there is no htm file, then collect a txt file as an alternative.
            elif "txt" in partial_link:
                table_info[i].append("https://www.sec.gov" + partial_link)

            if len(table_info[i]) > 4:
                table_info[i].pop()
    return table_info


if __name__ == '__main__':
    main()
