#!/usr/bin/env python
# coding: utf-8

# # Working with Metadata, Creating Text Networks
# 
# The previous notebooks focus on working directly with *EarlyPrint* texts, as data. But we also provide a range of tools for working metadata: information about the texts. Using metadata, we can supplement our study of texts with information about who authored a text, when it was published, who the printers and publishers were, and more. Knowing how to retrieve this metadata and combine it with the data from the text itself is a crucial skill for working with the *EarlyPrint* corpus.
# 
# Much of the metadata for *EarlyPrint* is inherited from EEBO-TCP (the Text Creation Partnership), which is itself inherited from the ESTC (English Short Title Catalog). If these acronyms don't yet mean anything to you, I've written a blog post that covers [many aspects of our metadata and the improvements we've made to it](https://earlyprint.org/posts/cleaning-metadata.html). To make a long story short, our updated and improved metadata is [available in its own Github repository](https://github.com/earlyprint/epmetadata).
# 
# The *EarlyPrint* site offers a number of ways to explore our metadata. The most fine-grained is our [Catalog Search](https://ada.artsci.wustl.edu/catalog/) tool. You can also browse and download facets of metadata using our [Download page](https://earlyprint.org/download/).
# 
# In this tutorial, we'll cover the following:
# 
# - where to download metadata
# - how to parse, or process, metadata XML
# - using our improved metadata to create networks of texts and their printers
# 
# ## Downloading Metadata
# 
# If you look at our [Catalog Search](https://ada.artsci.wustl.edu/catalog/) or [Download page](https://earlyprint.org/download/), you'll see that you can search through various metadata fields and download a CSV (comma-separated value) file of just the subset of metadata you care about. You can use this to get metadata just on texts published in a single year, or ones just by a certain author or on a certain subject.
# 
# For many coding workflows, you may want to do the same sort of operation from within a Python environment. Start with the complete set of metadata, carve out a subset you care about, and use that subset to do something else.
# 
# The files used in this tutorial can be found in [the standalone metadata Github repository](https://github.com/earlyprint/epmetadata). From the Github page, you can download all the files as `.zip` archive, or you can "clone" the repository onto your own computer.
# 
# For this first part of the tutorial, you'll need to install `lxml` by running `pip install lxml` on the command line. You may already have it installed from our previous tutorials. All subsequent libraries can be installed the same way. For help on this, see the *Programming Historian*'s [Installing Python Modules with pip](https://programminghistorian.org/en/lessons/installing-python-modules-pip).
# 
# ## A Single Metadata File
# 
# If there's just one text you care about, you can download our metadata directly into a Python script using the `requests` module. If you've already found or downloaded a text using the *EarlyPrint* library or lab, you'll notice that each text comes with a unique ID number, inherited from the TCP. (If you're working with our XML files, the ID is also the filename.)
# 
# As an example, let's find metadata for the text we used in our first tutorial, Margaret Cavendish's *Observations Upon Experimental Philosophy* and *The Blazing World*. The TCP ID for this text is A53049. Using that and the base url for our metadata GitHub repository, we can retrieve the metadata XML in just a few lines of code:

# In[1]:


# Import libraries

from lxml import etree
import requests


# In[2]:


tcp_id = "A53049"

# A "formatting" string that lets us put any TCP ID we want into the right place
base_url = f'https://raw.githubusercontent.com/earlyprint/epmetadata/master/header/{tcp_id}_header.xml'

# Using requests, "get" the text from the file at this web location
raw_text = requests.get(base_url).text
print(raw_text)


# We've now retrieved the XML from our metadata file for this text. Note that it's very short but includes lots of key information about the text, including its author, title, and date of publication. It also includes information from the text's imprint, including (in this case) the name of the printer.
# 
# Since this is an XML file, we can retrieve information from it using `lxml` in much the same way as we did when we parsed the text in our earlier tutorial.

# In[3]:


parser = etree.XMLParser(collect_ids=False, encoding='utf-8')
nsmap={'tei': 'http://www.tei-c.org/ns/1.0'}

# Parse your XML file into a "tree" object
metadata = etree.fromstring(raw_text.encode('utf8'), parser)

# Get information from the XML

# Get the title, using .find()
print("Title:", metadata.find(".//tei:sourceDesc//tei:title", namespaces=nsmap).text, "\n")

# Get the author, using the same technique
print("Author:", metadata.find(".//tei:sourceDesc//tei:author", namespaces=nsmap).text, "\n")

# Get the original date, as it was entered by catalogers
print("Original Date:", metadata.find(".//tei:sourceDesc//tei:date", namespaces=nsmap).text, "\n")

# Get the 4-digit EarlyPrint parsed date, using .get()
print("Parsed Date:", metadata.find(".//tei:sourceDesc//tei:date", namespaces=nsmap).get("when"), "\n")

# Get the printer by finding based on the "type" attribute
print("Printer:", metadata.find(".//tei:person[@type='printer']/tei:persName", namespaces=nsmap).text, "\n")


# ## All of the Metadata
# 
# The above method works fine if you need data on just one text, but what about analyzing the data for *all* of the texts at once? To do this, you'll need to [download all of the metadata files from Github](https://github.com/earlyprint/epmetadata). But once you do, the code is not all that different from working with a single file.
# 
# In the following code block, we'll get the title, author, and date for every single text in the *EarlyPrint* corpus. We'll aggregate the information and store it in a `pandas` DataFrame for later use and analysis. For more on `pandas`, see their [documentation](https://pandas.pydata.org/).
# 
# *n.b. Some of the dates  in our corpus are ranges rather than exact years, which are handled by `notBefore` and `notAfter` attributes of the `<date>` element. I'm skipping over those in this example, but you may want to retain them in your analysis. Find out more in [my metadata blog post](https://earlyprint.org/posts/cleaning-metadata.html).*

# In[4]:


import pandas as pd
import glob

# Get the full list of metadata files
# (You'll change this line based on where the files are on your computer)
files = glob.glob("../../epmetadata/header/*.xml")

all_data = [] # Empty list for data
index = [] # Empty list for TCP IDs
for f in files: # Loop through each file
    tcp_id = f.split("/")[-1].split("_")[0] # Get TCP ID from filename
    metadata = etree.parse(f, parser) # Create lxml tree for metadata
    title = metadata.find(".//tei:sourceDesc//tei:title", namespaces=nsmap).text # Get title
    
    # Get author (if there is one)
    try:
        author = metadata.find(".//tei:sourceDesc//tei:author", namespaces=nsmap).text
    except AttributeError:
        author = None
    
    # Get date (if there is one that isn't a range)
    try:
        date = metadata.find(".//tei:sourceDesc//tei:date", namespaces=nsmap).get("when")
    except AttributeError:
        date = None
    
    # Add dictionary of data to data list
    all_data.append({'title':title,'author':author,'date':date})
    
    # Add TCP ID to index list
    index.append(tcp_id)


# Create DataFrame with data and indices
df = pd.DataFrame(all_data, index=index)
df


# ## Trimming and "Cleaning" Data Fields
# 
# Though we've done a lot of work to make the *EarlyPrint* data more usable, some fields may still need to be adjusted, trimmed, or edited before they can be analyzed. The Author field, for example, includes birth and death dates for most authors, which a researcher may want to leave out.
# 
# There's no one-size-fits-all approach to doing this sort of adjustment. And though this step is often referred to as "data cleaning," the task of deciding when and how to "clean" and aggregate data is [important intellectual work](http://curatingmenus.org/articles/against-cleaning/) with serious research implications. How you "clean" data fields will depend on your research question.
# 
# Below, I focus on a single data field that we'll use in the next section: the names of printers. As I discuss in the [metadata post](https://earlyprint.org/posts/cleaning-metadata.html), the *EarlyPrint* metadata takes imprint information a step further by algorithmically parsing out the names of printers, publishers, and booksellers (among others). This process is imperfect, and it leaves some unneccessary characters and unusual spellings in these data fields.
# 
# Consider these spelling variants for the name of printer Thomas Newcomb:
# 
# ```
# Thomas Newcomb
# Tho. Newcomb
# T[homas] N[ewcomb]
# Tho: Newcomb
# ```
# 
# Ideally, we would want any analysis of printers to recognize that these 4 variants refer to the same person. We can do that by standardizing the data field as we process it. We can create a function to do this:

# In[21]:


# Import some built-in libraries
import re, json

# Get a list of standard early modern first name abbreviations, and what they stand for
with open("name_abbrev.json", "r") as abbrevfile:
    name_abbrev = json.loads(abbrevfile.read())

def standardize_name(name): # Define our function
    name = name.replace("[","").replace("]","") # Remove bracket characters
    name = name.strip(",'") # Remove commas and apostrophes from the beginning or end of the name
    name = name.replace("Iohn", "John") # Replace Iohn with John (a common spelling variant)
    # Finally, look through each abbreviation and, if found,
    # replace it with the full first name.
    for k,v in name_abbrev.items():
        name = re.sub(f"{k}[^a-zA-Z\s]", f"{v}", name)
    return name


# ## Building a Network
# 
# Now that we've created a function for cleaning up the printer names, we can use them for any purpose we like. In the rest of this tutorial, we'll use printer names to create a network visualization of printers and the books they printed. Such a visualization could be useful for determining how much collaboration among printers there is in the early modern period.
# 
# Networks are made up of **nodes** or entities, and the **edges** or relationships that connect those entities to one another. If you're new to networks, you might refer to [this *Programming Historian* tutorial on working with networks in Python](https://programminghistorian.org/en/lessons/exploring-and-analyzing-network-data-with-python). We'll use a similar Python approach here.
# 
# Our goal is to create a **bipartite** network, one with two different types of nodes: printers and the books they printed. To quickly create a network, we can build an **edgelist** from our metadata, which is simply a list of which entities are related or linked.
# 
# Just as we did when getting author, title, and date above, we can loop through every metadata file and pull out the TCP ID and any printers attached to that text. As we do, we can also "clean" the printer names using our function above. Each connection between a TCP ID (representing a book) and a printer's name becomes an item in our edgelist.

# In[22]:


edgelist = [] # Create an empty list
for f in files: # Loop through each file
    tcp_id = f.split("/")[-1].split("_")[0] # Get TCP ID from filename
    metadata = etree.parse(f, parser) # Create lxml etree object
    
    # Get a list of all printer's names
    printers = metadata.findall(".//tei:person[@type='printer']/tei:persName", namespaces=nsmap)
    
    # Get the date of the printing (if there is one)
    try:
        date = metadata.find(".//tei:sourceDesc//tei:date", namespaces=nsmap).get("when")
    except AttributeError:
        date = None
    
    # Add each printers name to the edgelist
    for p in printers:
        edgelist.append((tcp_id, standardize_name(p.text), {'date':date}))
        
print(edgelist)


# The results above show the full list of edges as Python tuples. The first item in an edge is a TCP ID for a text, the second is the name of the printer, and the third is a dictionary of any attributes (in our case, that's just the date of publication).
# 
# Next, using the Python library `networkx`, we can create a network or **graph** object to hold all of our node and edge information.

# In[23]:


import networkx as nx # Import networkx

B = nx.Graph() # Create an empty graph object

# Create lists of our two node types
texts = []
printers = []
for e in edgelist:
    texts.append(e[0])
    printers.append(e[1])

# Make sure names or IDs don't repeat
texts = list(set(texts))
printers = list(set(printers))

# Add each node list to our graph, with bipartite and group attributes to keep track of which is which
B.add_nodes_from(texts, bipartite="text", group=1)
B.add_nodes_from(printers, bipartite="printer", group=2)

# Add edge list to our graph
B.add_edges_from(edgelist)
print(nx.info(B))


# In the code above, we created our network and printed some basic information about it. 
# 
# The network has 30,473 nodes, which includes both texts and printers. Considering all of the printer names are included, that means the network has far fewer texts than the ~52,000 records in the *EarlyPrint* corpus. This makes sense because a lot of texts have no publication or imprint information at all, and of the ones that do, only some of them name the printer.
# 
# And the network has 29,724 edges, which means that nodes on average have fewer than 2 connections. Again, this makes sense based on what we know about the print record: most books that name a printer name just one person. This also means our network has low **density**: it is sparse because there are few edges compared to the number of nodes. This isn't all that unusual for bipartite networks, but it will help us to know what to expect when the network is visualized, as we'll see in a moment.
# 
# Before we can move on to visualization, it will be helpful to add more information about each text to our network. A TCP ID doesn't tell the researcher about the text itself. To do this, we can return to the `pandas` DataFrame that we created at the beginning of this tutorial.

# In[24]:


for n,d in B.nodes(data=True): # Loop through every node in the network
    if d['bipartite'] == 'text': # If the node is a text (and not a printer)
        
        # Create an attribute for the book's title, author, and date, and
        # populate those attributes with corresponding information from
        # our pandas DataFrame (df)
        B.nodes[n]['book_title'] = df.loc[n]['title']
        B.nodes[n]['author'] = df.loc[n]['author']
        B.nodes[n]['date'] = df.loc[n]['date']
        
        # Create a special 'title' attribute with all this information combined
        # This is so it will display in our visualization
        B.nodes[n]['title'] = f"{df.loc[n]['title']}<br>{df.loc[n]['author']}<br>{df.loc[n]['date']}"


# ## Visualizing the Network
# 
# We could write a few lines of code to display our full network, but with 30,000+ nodes our visualization is likely to come out a wieldy, muddled mess. It will be more productive to create a smaller subset of the network to visualize, making things easier to read and interpret. Let's look at the network just for the year 1660.

# In[25]:


# Get all the edges for 1660
edges_1660 = [(source,target) for source,target,d in B.edges(data=True) if d['date'] is not None and int(d['date']) == 1660]

# Use the edge_subgraph() function to create a subset of the larger network
subgraph_1660 = B.edge_subgraph(edges_1660)
print(nx.info(subgraph_1660))


# We're finally ready to visualize our network. We can do this with the wonderful [`pyvis` library](https://pyvis.readthedocs.io/en/latest/index.html), which lets us create interactive visualizations inside Jupyter notebooks.

# In[26]:


from pyvis.network import Network # Import pyvis

# Create an empty pyvis graph
g = Network(width=800,height=800,notebook=True,heading='')

# Load our networkx graph into pyvis
g.from_nx(subgraph_1660)


# In[27]:


# Display the resulting graph in our notebook
g.show("subgraph.html")


# You can scroll to zoom in and out of the network visualization, and you can click and drag to pan. 
# 
# As you zoom in, labels will appear on each node. If you click on a node, you'll highlight that node and its connected edges. Blue nodes represent texts, and yellow/orange ones represent printers.
# 
# If you hold your mouse over a blue text node, you'll see a pop up with the title, author, and date of the book. That's the information we added in the code above!
# 
# Right away there are several things to take away from this visualization. Our initial question was: how often do printers collaborate with one another on the same book? In this network, we see lots of disconnected **components**, little network "islands" with just one orange printer connected to a set of blue books. It's safe to say that, at least in 1660, it was far more common for printers to work alone than to collaborate with another press.
# 
# But this wasn't always the case. Zooming in one of the larger components, we find this:
# 
# ![](component.png)
# 
# Francis Tyton, John Macock, and John Streater are grouped together in a single close-knit component. They're not printing every single one of these texts together, but most of these texts are connected to at least two of these three printers. And interestingly, most of these texts are proclamations from the monarch or other royal publications (the most common type of co-printed text in the year 1660).
# 
# A natural question to ask next would be: can we see more co-printing when we widen the timespan of the network? You could do this by increasing the date range in the subgraph code above to a decade or longer, for example:
# 
# ```
# edges_1660s = [(source,target) for source,target,d in B.edges(data=True) if d['date'] is not None and int(d['date']) > 1659 and int(d['date']) < 1670]
# ```
# 
# Keep in mind that the wider your date range is, the more nodes and edges there will be. This could make the graph run very slowly in your browser and/or make it difficult to read. You could certainly also record this information in a `pandas` DataFrame or another format and count up the co-printed texts directly: there are many paths to answering this question and not all of them need go through network visualization. But as we can see, our network is a quick and effective way toward building an intuition about 17th-century printing and exploring data that can generate new, better research questions.
# 
# *n.b. I tested out the network for the whole decade of the 1660s, and there wasn't much more collaboration among printers than there was in 1660 alone. But different network "slices" might reveal different results.*
# 
# ## Next Steps
# 
# We've looked at just a couple examples of how metadata might be processed and used in Python. The DataFrame and network visualization methods here give a rough outline of what might be done with metadata after it's parsed from our XML, but there are a large number of computational possibilities for this data. Perhaps most importantly, you now know how to find and access this data in order to supplement your work with our texts, as demonstrated in the other tutorials.
# 
# The exploratory methods outlined here are meant to be an intermediate step rather than an ending. Which is to say, creating a network visualization might prompt you to return to earlier stages of scholarly work and data analysis. Let's look at an example by zooming in on a different component in our interactive visualization:
# 
# ![](component2.png)
# 
# In this component we find the printer Thomas Newcomb, whose often-abbreviated name we dealt with in our name reconciliation, data "cleaning" step. We can see here that his frequent collaborator is the printer Edward Husbands. But there's an additional, different printer for just one text in this component: Edward "Husband" with no "s." This is very likely the same person as Edward Husbands, with his name misspelled in one of the imprints. 
# 
# It may have been difficult to find this misspelling without our network visualization. We could have used a text analysis technique such as edit distance to find variants, but that could still involve scanning a large list of texts (even for just one year) that were printed by a single person. Our network draws together co-printings, and in doing so it reveals name variants that are likely to refer to the same person. If we hadn't regularized "Tho. Newcomb" to "Thomas Newcomb," we would have found that name in this component, too!
# 
# Rather than being a culmination or stopping point for our analysis, the visualization can instead help us to rethink our data organization practices, to catch things we may have missed, and to suggest new ways of moving through the data. In future tutorials we'll continue to use this metadata to complement our work with the texts, keeping in mind the lessons we've learned here.
