import csv
import requests
from bs4 import BeautifulSoup
import time

URL = 'http://www.dgii.gov.do/app/WebApps/ConsultasWeb/consultas/placa.aspx'

class DgiiOposicionVehiculo():

    def __init__(self):
        self.url = URL
        response = requests.get(self.url).text
        self.soup = BeautifulSoup(response,"lxml")   
        viewstate = self.soup.select("#__VIEWSTATE")[0]     
        if not viewstate:
            return
            
        self.viewstate = viewstate['value']
        self.eventvalidation = self.soup.select("#__EVENTVALIDATION")[0]['value']
        
    def __read(self, identification, placa):
        for title in self.soup.select("#ctl00_cphMain_pBusqueda"):
            search_item = title.text

            headers= {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                      'Content-Type':'application/x-www-form-urlencoded',
                      'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

            formfields = {
                            'ctl00$smMain': 'ctl00$upMainMaster|ctl00$cphMain$btnConsultar',
                            'ctl00$cphMain$txtRNC': identification,
                            'ctl00$cphMain$txtPlaca': placa,
                            '__VIEWSTATE': self.viewstate,
                            '__EVENTVALIDATION':self.eventvalidation,
                            '__EVENTTARGET': '',
                            '__EVENTARGUMENT': '', 
                            '__ASYNCPOST': 'true',
                            'ctl00$cphMain$btnConsultar': 'Consultar'
                        }

            #here in form details check agra , i am able to scrape one city only,
            # how to loop for all cities
            res = requests.post(self.url, data=formfields, headers=headers).text
            soup = BeautifulSoup(res, "html.parser")

            data = []
            table = soup.find('table', attrs={'id':'ctl00_cphMain_gvDetallesPlaca'})
            if table is not None:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    if(len(cols) > 0):
                        data.append([ele for ele in cols if ele])

            return data

    def search_from_array(self, array_data = []):
        self.consult_data = array_data
        total = len(self.consult_data)
        counter = 0
        for data in self.consult_data:
            counter += 1
            print('Procesando {0} de {1}'.format(counter, total))
            yield self.__read(
                data['identification'],
                data['placa']
            )

    def search_from_cursor(self, cursor):
        counter = 0

        while True:
            row = cursor.fetchone()
            if not row or len(row) == 0:
                break

            counter += 1
            print('Registros procesados: {0}'.format(counter))

            try:                
                yield self.__read(
                    row[0],
                    row[1]
                )
            except Exception as e:
                print('Registro fallido: ' + str(counter))
                yield []

