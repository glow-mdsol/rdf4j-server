# RDF4J-Server

This is the eclipse project that is used to maintain the [DPRR RDF server](http://romanrepublic.ac.uk/rdf).

It was created by [John Bradley (DDH/KCL)](https://github.com/johnBradley501/uk.ac.kcl.cch.dprr.rdf.server) in the first half of 2017 with a few minor changes a year later, and is used to provide the REF-oriented services for DPRR.

## Setting up the Server for Public Use

This server is built upon the workbench code from [rdf4j](http://rdf4j.org):

* it operates as a Java-based web application, and runs under Tomcat.
* rdf4j requires at least a Java-based web server that supports at least Java Servlet API 2.5 and Java Server Pages (JSP) 2.0, or newer. I have developed and tested it with Tomcat 8.0.
* rdf4j requires Java version 8.

The DPRR RDF app can be packaged as a .war file, and then set up using Tomcat's WAR file support. A suitable WAR file can be readily exported from this Eclipse project. I recommend it should be called "rdf.war", and put in the project's "war" subfolder.

In the default version of this app, RDF data is fetched from `/usr/local/etc/rdf4j`. Within this folder is the rdfj4 repository folder called `dprr`, which is used as the source for the RDF data to be served.
Both the folder for RDF repositories and the particular folder can be changed by editing file `/WEB-INF/server.config`.

See information below about how to get data from DPRR's Postgres database into suitable RDF format.

## URI mapping requirements

It is one of the four basic Linked Data requirements that a user needs to be able to enter a URI for an entity, and receive useful data back. URIs for entities in DPRR's RDF data all begin `http://romanrepublic.ac.uk/rdf/entity`, with `entity` being the path component recognised by DPRR RDF Server as a request for entity data.

[http://romanrepublic.ac.uk/rdf/ontology](http://romanrepublic.ac.uk/rdf/ontology) is described as a request for the DPRR ontology, and [ http://romanrepublic.ac.uk/rdf/endpoint ](http://romanrepublic.ac.uk/rdf/endpoint) is a request to access the data-oriented SPARQL endpoint. [ http://romanrepublic.ac.uk/rdf/doc ](http://romanrepublic.ac.uk/rdf/doc) is a request to access the documentation about the DPRR RDF Server.

All of rdf4j's native functionality that is supported within DPRR RDF server should begin with `http://romanrepublic.ac.uk/rdf/repositories/dprr`

Thus, all URLs that this tomcat application serves begin `http://romanrepublic.ac.uk/rdf` and the larger server environment needs to be set up so that `http://romanrepublic.ac.uk/rdf` is passed to this DPRR web application.

N.B.: It is important that all mapping from this URL prefix to whatever is needed to get the request to the web app should be done "behind the scenes", without changing the URL the user sees!!

## Differences between rdf4j workbench and the DPRR RDF server

The DPRR RDF server is built upon the rdf4j workbench code, but has several important differences:

1. the full rdf4j workbench supports not only the reading of RDF data, but also its changing. Hence, all the code that supports changing of the RDF data has been removed from the DPRR workbench
1. normally the workbench fetches all its data from a backing rdf4j RDF server. The workbench is then a user-friendly front end to operations that can be done against this backend server. In the DPRR server data is fetched from a representation of the RDF data directly in the file system (at `/usr/local/etc/rdf4j`) rather than through an intermediate RDF server. This is to prevent the world from being able to get at the RDF data through this intermediate server, where functions such as data changing, are provided. You can see the DPRR RDF server being pointed to the file system containing the DPRR RDF data rather than to an intermediate backing rdf4j server in `/WEB-INF/server.config` where the server is specified using a file: URL file:`/usr/local/etc/rdf4j`
1. some functionality has been added to the DPRR server by John Bradley. They are found in JAVA package `uk.ac.kcl.ddh.jb.rdf.server.servlet`, and referenced in the `WEB-INF/web.xml` file:

   1. an entity servlet (`EntityServlet`) allows users to pass URIs for DPRR data entities and receive back useful information either in the form of an HTML page, or a collection of RDF statements that are related to the specified entity. This is actually achieved by either making use of rdf4j's `ExploreServlet` for the HTML-oriented interface, or the added "subservlet" `RdfGenServlet` for the delivery of raw data.
   1. a SPARQL Endpoint servlet (`EndpointServlet`) provides data-oriented SPARQL endpoint services for users.
   1. a servlet that aims to serve the DPRR OWL Ontology is provided in `OntologyServlet`. See below.

1. The DPRR Ontology is made available through the web content folder `/ontology`.
   1. The ontology itself that is in there as `dprr.owl` is actually served to users through the rather trivial `OntologyServlet`.
   1. The documentation about the ontology, created by OWLDoc, is served from the folder `/ontology/doc`:
1. Perhaps the most significant change to rdf4j code, other than the removing of functions mentioned in point 1. above, is the addition of a handler for the rdf4j `RepositoryManager` used here. The code for this is in `uk.ac.kcl.ddh.jb.rdf.server.SharedRepositoryHandler`. It holds the `RepositoryManager` that gives program access to the rdf data (normally in `/usr/local/etc/rdf/`). See the description of this functionality in the next section of this file. To make use of `SharedRepositoryHandler` required minor changes in rdf4j-provided code in classes in `org.eclipse.rdf4j.workbench.proxy: WorkbenchGateway` and `WorkbenchServlet`, `org.eclipse.rdf4j.workbench.util.BasicServletConfig`, and `org.eclipse.rdf4j.workbench.base.TransformationServlet`. See more details below.
1. folder `WebContent/doc` has been added containing html and associated files and served by the web app. It provides user documentation about the DPRR RDF server.

## Removal of query saving support in workbench code: rdf4j's QueryServlet

The rdf4j workbench provides support for the saving and sharing of SPARQL queries between users. Although this is a lovely idea in many ways, it seemed to be to be a possible long term maintenance headache in the DPRR server.

Thus, code to support this was removed. It was easy to the remove the code in the web content files that presented this feature to the user on his/her browser. However, I chose to also remove support from the backing Java code in the rdf4j workbench. The change was made in `org.eclipse.rdf4j.workbench.commands.QueryServlet` by commenting out a private function altogether (lines 280-317), and then removing the code that referenced it lines 242-44. This code could have perhaps been left as rdf4j had delivered it since the web-content changes made its functionality invisible to the DPRR server user.

## uk.ac.kcl.ddh.jb.rdf.server.SharedRepositoryHandler

The `SharedRepositoryHandler` was added to deal with two problems that arose from the rdf4j code with regard to the RepositoryHandler. In the original rdf4j code the location of the source for RDF data and the particular repository for it was made available to the workbench code as Servlet InitParameter data for rdf4j's servlet `WorkbenchGateway` in `web.xml`:

```xml
<init-param>
    <param-name>default-server</param-name>
    <!--  param-value>/rdf4j-server</param-value -->
    <param-value>file:/usr/local/etc/rdf/</param-value>
</init-param>

<init-param>
    <param-name>default-path</param-name>
    <!-- param-value>/NONE/repositories</param-value -->
    <param-value>/dprr</param-value>
</init-param>
```

This worked well for the "native" rdf4j workbench since all the rdf4j functionality came through a single servlet called "workbench": `org.eclipse.rdf4j.workbench.proxy.WorkbenchGateway`.

However, in the DPRR RDF server it was most expedient to add two other servlets for entity display and for the basic SPARQL endpoint service (`EndpointServlet` and `EntityServlet`) in addition to
`WorkbenchGateway`, and they didn't have access to the init parameters for `WorkbenchGateway`.

In addition, and even more serious, the rdf4j RepositoryHandler (`LocalRepositoryHandler`) that provided program access to the RDF repository only allowed one rdf4j Repository class to be instantiated (this was not true if the intermediate rdf4j server was used instead -- but see item 2., above).

As a result, this one instance had to be shared between the rdf4j's surviving workbench code, and the servlets developed specifically for the DPRR RDF server: `EndpointServlet` and `EntityServlet`.

Thus, the `SharedRepositoryHandler` code was developed that took its repository information from `/WEB-INF/server.config` rather than from Servlet `InitParameters`. It created and held an rdf4j `RepositoryHandler` instance that could be accessed by both rdf4j and DPRR RDF servlets.

The effect to rdf4j was that the default-server and default-path parameters have been removed from the `/WEB-INF/web.xml` file for DPRR RDF, and the rdf4j code changed in a few places so that the data for the location of the RDF repository is now taken from the SharedRepositoryHandler rather than from Servlet `InitParameters`.

## Changes to rdf4j code

The following changes have been made to rdf4j code to make use of SharedRepositoryHandler:

* org.eclipse.rdf4j.workbench.proxy.WorkbenchGateway: methods getDefaultServerPath() and init()
* org.eclipse.rdf4j.workbench.proxy.WorkbenchServlet: method init()
* org.eclipse.rdf4j.workbench.util.BasicServletConfig: constructor BasicServletConfig(String name, ServletContext context)
* org.eclipse.rdf4j.workbench.base.TransformationServlet: method init()

## Preparing data for serving as RDF

There are two stages to this operation: (1) converting the data in the Postgres DPRR database into a file containing RDF triples using the d2rq toolkit, and (2) loading these triples into an rdf4j managed RDF repository using rdf4j's console tool.

### Creating the RDF Triples

There is some information about this task in the public description of the DPRR RDF server at [http://romanrepublic.ac.uk/rdf/doc](http://romanrepublic.ac.uk/rdf/doc). See tab "Building the Server".

N.B: This process assumes that the Postgres database structure is THE SAME as that used when the process was defined. If the structure is changed, the d2rq "mapping file" (see below) needs to be changed to reflect the changes in the DB's structure before the triples can be satisfactorily exported.

The [d2rq toolkit](http://d2rq.org/) is used as the mapping engine from the DB to RDF. It requires a "mapping file" [see documentation](http://d2rq.org/d2rq-language) to guide the translation, and this file has been created so that d2rq tools can be used (see below) to generate a set of raw RDF triples. However, d2rq, by itself, does not create the actual version of RDF data that is to be loaded. There is, then, a 2nd step involving a Python script to complete the preparation.

#### Using d2rq to create base RDF triples

Use [d2rq's dump-rdf tool](http://d2rq.org/dump-rdf) to export data into RDF. I use the command line

```bash
dump-rdf -f TURTLE -b http://romanrepublic.ac.uk/rdf/entity/ -o dprr_dump.ttl dprr-map.ttl
```

for this purpose. Note the following:

1. `-f`: the format needs to be TURTLE format for the Python script (see below) to work.
1. `-b`: the given base URI causes all data entities to be given the required URI prefix in the exported RDF.
1. `-o`: the generated RDF triples are put into the file `dprr_dump.ttl`.
1. the conversion is controlled by the mapping file `dprr-map.ttl`, which is available from this project's "misc" subfolder.

`dump-rdf` connects directly to DPRR's postgres database for this operation. Be sure to put appropriate credentials into the `dprr-map.ttl` file before running it.

Finally, on my machine this process runs for a long time (more than 10 minutes). Expect this.

#### Creating final RDF triples with Python file

A python script takes the RDF triple data created by `dump-rdf` and "cleans it up". First, it creates names for DPRR persons that match the names used in the Django-based web app, and approved by the DPRR historians. It also does some other minor fixups, including eliminating the many "empty" triples that dump-rdf creates.

The script is called `processttl.py` and can be found in this project's `misc` subfolder. It also connects directly to the database to get the information needed to create the DPRR person names. Be sure, then, to put appropriate credentials into the file.

The data generated as cleaned up RDF triples is put into the file `dprr_clean.ttl` by the script.

### Loading RDF into rdf4j repository

Having created the triples, and stored them in `dprr_clean.ttl`, one uses rdf4j's console program to create a suitable RDF repository. The console program is described at [http://docs.rdf4j.org/server-workbench-console/](http://docs.rdf4j.org/server-workbench-console/).

Be aware the DPRR's rdf4j repository contains a reasoner that allows the rules in DPRR's ontology to enrich the data display and SPARQL querying. To enable the reasoner, the DPRR repository is set up as a `memory-rdfs-dt` type (see section 2.1.3 of the console documentation mentioned above). Thus, BOTH the DPRR ontology and the data needs to be loaded.
You can find the ontology file in the WebContent as file `dprr.owl` in the ontology folder.

Because of a quirk in the console, `dprr.owl` must have a `ttl` file extension. Thus, it is necessary to copy the file from there and give the copy a new name, say `dprr-ont.ttl`.

One interacts with console through a serious of commands. Here are the ones I use (on my Windows machine) to load the new data:

```bat
connect d:\data\rdf4j
show repositories
open dprr
verify D:\research\DPRR\d2rq-0.8.1\dprr_clean.ttl
verify d:\research\DPRR\Ontology\dprr-ont.ttl
clear
load d:\research\DPRR\Ontology\dprr-ont.ttl
load D:\research\DPRR\d2rq-0.8.1\dprr_clean.ttl
```

Comments:

1. First, I connect to the place on my machine where rdf4j repositories are stored. I have suggested on the actual Linux based server this should be `/usr/local/etc/rdf4j`, in which case the command would be `connect /usr/local/etc/rdf4j`.
1. The `show repositories` command is not necessary, but will ensure that you are pointing at the right place. console should respond with at least two repositories - the existing "dprr" repository and the "SYSTEM" repository.
1. If all is OK so far, use the `open dprr` command to point at the dprr repository.
1. Next, I run the verify command, pointing at the `dprr_clean.ttl` file created above to ensure that it is all properly formed RDF. I also verify the `dprr-ont.ttl` file that contains the DPRR ontology.
1. Then, it is time to use the `clear` command to discard the old RDF repository data.
1. Next, load the DPRR ontology.
1. Finally, load the triples.
