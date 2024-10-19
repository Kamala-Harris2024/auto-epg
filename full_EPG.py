import xml.etree.ElementTree as ET
import glob
import gzip

def merge_xmls(input_folder, output_file):
  root = ET.Element("tv")
  
  for filename in glob.glob(input_folder + "*.xml"):
    tree = ET.parse(filename)
    for element in tree.getroot():
      root.append(element)

  tree = ET.ElementTree(root)
  tree.write(output_file, encoding="utf-8", xml_declaration=True)


def gzip_file(filename):
  with open(filename, 'rb') as f_in:
    with gzip.open(filename + '.gz', 'wb') as f_out:
      f_out.writelines(f_in)


if __name__ == "__main__":
  input_folder = "guides/"
  output_file = "guide.xml"

  merge_xmls(input_folder, output_file)
  gzip_file(output_file)
  
  print(f"XML files were merged in {output_file} and compressed {output_file}.gz")
  