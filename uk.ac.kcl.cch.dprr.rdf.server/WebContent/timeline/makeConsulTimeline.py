# This Python script demonstrates how to use DPRR RDF server to fetch data tailored to a particular query
# and transform this data into an HTML display page (here, using Google Graphs tools)
#                ... John Bradley DDH/KDL    June 2017

import urllib2
import json

path = "research/dprr/timeline/"
fileName = "consuls.html"
urlBase = "http://romanrepublic.ac.uk/rdf/endpoint"
uriBase = "http://romanrepublic.ac.uk/rdf/entity/"

def getData():
    query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX vocab: <http://romanrepublic.ac.uk/rdf/ontology#>
select ?startDate ?endDate ?tname ?aid ?pid ?pname
where {
  ?person a vocab:Person;
     vocab:hasID ?pid;
     rdfs:label ?pname.
  ?tribeassert a vocab:TribeAssertion;
    vocab:isAboutPerson ?person;
    vocab:hasTribe ?tribe.
  ?postAssert a vocab:PostAssertion;
    vocab:hasID ?aid;
    vocab:isAboutPerson ?person;
    vocab:hasOffice <http://www.romanrepublic.ac.uk/rdf/entity/Office/3>;
    vocab:hasDateStart ?startDate;
    vocab:hasDateEnd ?endDate.
  ?tribe a vocab:Tribe;
    vocab:hasName ?tname.
}"""
    url = urlBase+"?query="+urllib2.quote(query.strip())
    req = urllib2.Request(url)
    req.add_header('Accept', "application/json")
    conn = urllib2.urlopen(req)
    rslt = json.loads(conn.read())
    conn.close()
    return rslt

def genBoringBit1(out):
    prefix = """<html>
    <!-- This page is generated by the demonstration Python script makeConsulTimeline.py available
    from http://www.romanrepublic.ac.uk/rdf/timeline             .. John Bradley   DDH/KDL  June 2017 -->
  <head>
    <!--Load the AJAX API-->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
    google.charts.load('current', {'packages':['timeline']});
    google.charts.setOnLoadCallback(drawChart);

    function drawChart() {
      var data = new google.visualization.DataTable();
      data.addColumn('string', 'Tribe');
      data.addColumn({ type: 'string', id: 'dummy bar label' });
      data.addColumn({'type': 'string', role: 'tooltip', 'p': {'html': true}})
      data.addColumn('date', 'Office Start Date');
      data.addColumn('date', 'Office End Date');

      data.addRows([
"""
    print >>out, prefix

def genBoringBit2(out):
    postfix = """
       ]);

      var options = {
        tooltip: { isHtml: true },
        title:'DPRR: Consuls by tribe',
        height: 900,
        timeline: {
          groupByRowLabel: true
        }
      };

      var chart = new google.visualization.Timeline(document.getElementById('chart_div'));

      chart.draw(data, options);
    }
    </script>
    <title>DPRR: Consuls by tribe</title>
  </head>

  <body>
    <h4>DPRR: Consuls by tribe</h4>
    <!--Div that will hold the timeline-->
    <div id="chart_div"></div>
  </body>
</html>
    """
    print >>out,postfix

def buildLabel(sdate, pid, aid, pname):
    rslt = '<b>Year</b>: '+str(-sdate)+' BCE<br />'
    rslt += '<b>Person</b>: '+pname+' ('+str(pid)+')<br />'
    rslt += '<b>PostAssertion ID</b>: '+str(aid)
    #rslt += '<b>Person</b>: <a href="'+uriBase+"Person/"+str(pid)+'">'+pname+'</a><br />'
    #rslt += '<a href="'+uriBase+"PostAssertion/"+str(aid)+'">Assertion</a>'
    #rslt = 'Year: '+str(-sdate)+' BCE'
    return rslt.replace("'", r"\'")

def genInterestingBit(out, data):
    bindings = data["results"]["bindings"]
    for binding in bindings:
        tname = binding["tname"]["value"]
        sdate = int(binding["startDate"]["value"])
        edate = int(binding["endDate"]["value"])+1
        pid = int(binding["pid"]["value"])
        aid = int(binding["aid"]["value"])
        pname = binding["pname"]["value"]
        print >>out, "   ['"+tname+"',\t'','"+buildLabel(sdate, pid, aid, pname)+"', new Date("+str(sdate)+",0,1), new Date("+str(edate)+",0,1)],"

out = open(path+fileName,"w")
genBoringBit1(out);
data = getData()
genInterestingBit(out, data);
genBoringBit2(out);
out.close()