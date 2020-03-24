---


---

<h1 id="recolección-y-almacenamiento-de-datos-de-ree.">Recolección y almacenamiento de datos de REE.</h1>
<p>Los datos recogidos corresponden a la Red Eléctrica Española y se distribuyen a través de la siguiente API:</p>
<p><a href="https://apidatos.ree.es/">API REE</a></p>
<h1 id="requisitos">Requisitos</h1>
<ul>
<li>Python3</li>
<li><a href="https://v2.docs.influxdata.com/v2.0/get-started/">InfluxDB</a></li>
<li><a href="https://requests.readthedocs.io/en/master/">Requests</a></li>
<li><a href="https://pendulum.eustace.io/docs/">Pendulum</a></li>
</ul>
<h2 id="configuración-de-influxdb">Configuración de InfluxDB</h2>
<p>Una vez instalado debemos de ejecutarlo con <code>influxd</code>, y accedemos desde el navegador al explorador de datos <code>localhost:9999</code>. Ponemos un nombre a la organización, creamos un bucket y buscamos el tocken de acceso.</p>
<p>Esta información ha de ser insertada en el comienzo del fichero principal.</p>
<pre><code>ORG = "US"  
TOKEN = "Token que se encuentra en el apartado Buckets/tokens
BUCKET = 'REE'  
</code></pre>
<h2 id="atributos-de-entrada">Atributos de entrada</h2>
<p>Utilizamos estas plantillas al final del fichero para hacer uso de la función que recolecta el conjunto de datos indicado. Hay 4 plantillas con 4 tipos de datos distintos, los relevantes para la practica son los dos primeros.<br>
<code>INPUT_TEMPLATE_DEMANDA</code>_1 y <code>INPUT_TEMPLATE_DEMANDA_2</code></p>
<pre><code>INPUT_TEMPLATE_DEMANDA_1 = {  
    "request_type": "DEMANDA",  
    "request_subtype": "Demanda real",  
    "start_date": [2017, 1, 1, 0],  
    "end_date": [2019, 12, 31, 0],
    "time_trunc": "hour",
    "measurement_unit": "KWh"  }

INPUT_TEMPLATE_PRECIOS_1 = {  
    "request_type": "PRECIOS",  
    "request_subtype": "PVPC (€/MWh)",  
    "start_date": [2017, 1, 1, 0],  
    "end_date": [2019, 12, 31, 0],
    "time_trunc": "hour",
    "measurement_unit": "€/MWh"  }
</code></pre>

