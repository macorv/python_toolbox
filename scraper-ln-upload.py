# Importamos las librerias necesarias para construir el scrapper
import requests #Para bajar el HTML
import bs4 # Para parsear el HTML
import time # Para grabar fecha
import datetime # Para grabar fecha y hora
import os # Para crear carpeta

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuraciones Requests
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

####----####

# Parametros configurables
# Guardo en un archivo de texto, para tener registro de las ejecuciones
carpetaBase = '/path/to/scraper-log/'

# Armo el nombre del archivo en base a la fecha en que se corre. Es el log del archivo
fileNameBase = 'Ejecucion_'

# URL de busqueda
urlBase = 'https://buscar.lanacion.com.ar/'

# Opciones de busqueda para la nacion
urlOpciones = ["economia/c-Econom%C3%ADa"]
#urlOpciones = [ "politica/c-Pol%C3%ADtica", "economia/c-Econom%C3%ADa" , "turismo/c-Turismo"]

# Opciones de busqueda para las fechas (este parametro puede ser automatizado)
urlFecha = ['date-20180101,20180829','date-20170601,20171231','date-20170101,20170531','date-20160601,20161231', 'date-20160101,20160531','date-20150601,20151231', 'date-20150101,20150531','date-20140601,20141231', 'date-20140101,20140531','date-20130601,20131231', 'date-20130101,20130531','date-20120601,20121231', 'date-20120101,20120531','date-20110601,20111231', 'date-20110101,20110531','date-20100601,20101231', 'date-20100101,20100531']

# Opciones de pagina (este parametro puede ser automatizado)
urlPaginas = 401

# Visual para saber que empieza
print("Empieza")

# Obtengo la fecha
ts = time.time()

# Armo la fecha
fileNameDate = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

# Armo el nombre
fileName = carpetaBase + fileNameBase + fileNameDate + '.txt'
print("Nombre del archivo:", fileName)

# Declaro la variable para manejar el archivo
file = open(fileName,'w+')

# Mensaje para saber que se esta haciendo
print("Vamos a ver noticias de: " + urlBase )
file.write("Vamos a ver noticias de: " + urlBase + '\n\n' )

# Defino funcion para que me saque los videos de las notas
# Hay que mejorarlo!!!
def not_video(tag):
    return not tag.div

# Ahora la idea es recorrer cada categoria que esta en el parametro de urlOpciones
# Dentro de cada parametro, vamos a traer los links de cada pagina
# Y de cada URL sacamos el texto, solo nos interesa la nota

for seccion in urlOpciones:
    seccionSplit = seccion.split('/')[0]
    pathCarpeta = './articulos/'+seccionSplit
    '''Creamos la carpeta donde se van a guardar los articulos'''
    os.makedirs(pathCarpeta, exist_ok = True)
    print("Para la seccion: " + seccionSplit)
    file.write("Para la seccion: " + seccionSplit + '\n' )
    '''Ahora tengo que recorrer cada pagina '''
    for fecha in urlFecha:
        for pagina in range(1,urlPaginas,5):
            print("Tengo en pagina: ", pagina)
            '''Armo la URL de donde voy a traer las noticias'''
            urlParaRevisar = urlBase + seccion + '/' + fecha + '/page-' + str(pagina)
            print("La url es: " + urlParaRevisar)
            file.write("\t La url es: " + urlParaRevisar + '\n' )
            '''Requests sobre la pagina'''
            lnPagBuscador = session.get(urlParaRevisar)
            try:
                lnPagBuscador.raise_for_status()
            except Exception as exc:
                print('Hubo un problema: %s' %exc)
                file.write("\t\t Error en este link" + '\n')
            '''Me aseguro que el encoding sea el correcto, tiene que estar en Español'''
            lnPagBuscador.encoding = 'utf-8'
            '''Empiezo a parsear con BeautifulSoup el archivo HTML'''
            lnSoup = bs4.BeautifulSoup(lnPagBuscador.text, 'html.parser')
            '''Busco la parte del HTML donde se encuentran los links a las notas. Se guarda en una lista'''
            elems = lnSoup.select('span > h2 > a')
            '''Me quedo unicamente con los links a las notas'''
            for k,i in enumerate(elems):
                '''Empiezo a recorrer la lista de URLs para bajarme el texto'''
                urlParaBajar = elems[k].get('href')
                print('Bajando HTML de: ' + urlParaBajar)
                file.write("\t\t" + 'Bajando HTML de: ' + urlParaBajar  + '\n' )
                nombreArticulo = urlParaBajar.split('/')[3]
                articulos = open(pathCarpeta + '/' + nombreArticulo + '.txt', encoding = 'utf-8', mode = 'w+')
                lnArticulo = requests.get(urlParaBajar)
                try:
                    lnArticulo.raise_for_status()
                except Exception as exc:
                    print('Hubo un problema: %s' %exc)
                    file.write("\t\t Error en este link" + '\n')
                '''Empiezo a bajar cada HTML'''
                lnArticulo.encoding = 'utf-8'
                notaSoup = bs4.BeautifulSoup(lnArticulo.text, 'html.parser')
                textoNota = notaSoup.select('section[id="cuerpo"] > p')
                for texto in textoNota:
                    if not_video(texto) == True:
                        ext = texto.get_text(' ',strip=True)
                        print('Guardando texto en archivo...')
                        file.write('Guardando texto en archivo...')
                        articulos.write(ext + '\n')
                        print('Listo')
                        file.write('Listo')
                    else:
                        continue
                articulos.close()


print("Termino")
file.close()
