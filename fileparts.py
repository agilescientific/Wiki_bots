file_header = """<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.8/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.8/ http://www.mediawiki.org/xml/export-0.8.xsd" version="0.8" xml:lang="en">"""

article_header = """  
  <page>
    <title>{0}</title>
    <ns>0</ns>
    <revision>
      <contributor>
        <username>Matt</username>
      </contributor>
      <comment>Imported article. Testing import process.</comment>
      <text xml:space="preserve">"""
      
# Need double curlies to use string's format method
infobox = """{{{{{0} 
 | {1} = {2}
 | {3} = {4}
 | {5} = {6}
 | {7} = {8}
 | {9} = {10}
}}}}
"""

article_footer = """</text>
      <model>wikitext</model>
      <format>text/x-wiki</format>
    </revision>
  </page>"""

file_footer = """</mediawiki>"""
