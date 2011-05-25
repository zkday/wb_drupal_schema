#
#  wb_drupal_schema_grt.py
#  MySQLWorkbench
#
#  Created by Pedro Faria on 17/Jan/10.
#  Edit and completed by zkday on 24/May/2011
#

import re

# import the wb module, must be imported this way for the automatic module setup to work
from wb import *
# import the grt module
import grt

# define this Python module as a GRT module
ModuleInfo = DefineModule(name= "drupalDumpSchema", author= "zkday", version="1.1")

def getColumnDef(col):
  """docstring for getColumnDef"""
  opts = []
  p = re.search('([a-z]+)(?:\(([0-9]+)\))?', col.formattedType.lower())
  mtype = p.group(1)
  
  type = mtype
  
  if col.isNotNull:
    opts.append("'not null' => TRUE")
  
  if not col.defaultValueIsNull:
    if col.defaultValue:
      if col.defaultValue.isdigit():
        opts.append("'default' => %s" % col.defaultValue)
      else:
        opts.append("'default' => '%s'" % col.defaultValue)

  ''' set type length '''
  if mtype == 'int': pass
  elif mtype == 'tinyint':
    type = 'int'
    opts.append("'size' => 'tiny'")
  elif mtype == 'smallint':
    type = 'int'
    opts.append("'size' => 'small'")
  elif mtype == 'mediumint':
    type = 'int'
    opts.append("'size' => 'medium'")
  elif mtype == 'bigint':
    type = 'int'
    opts.append("'size' => 'big'")
  
  elif mtype == 'float': pass
  elif mtype == 'double':
    type = 'float'
    opts.append("'size' => 'big'")
  
  elif mtype == 'text':
    opts.append("'size' => 'normal'")
  elif mtype == 'tinyint':
    type = 'text'
    opts.append("'size' => 'tiny'")
  elif mtype == 'mediumtext':
    type = 'text'
    opts.append("'size' => 'medium'")
  elif mtype == 'longtext':
    type = 'text'
    opts.append("'size' => 'big'")
  
  elif mtype == 'numeric': pass
  elif mtype == 'decimal':
    type = 'numeric'
    
  elif mtype == 'char': pass
  
  elif mtype == 'varchar': pass
  
  elif mtype == 'longblob':
    type = 'blob'
    opts.append("'size' => 'big'")
  
  elif mtype == 'datetime': pass
  elif mtype == 'date':
    type = 'datetime'
  else: pass
    #raise Exception('Data type %s not supported on Drupal Schema. (%s.%s[%s])' % (mtype, col.owner.name, col.name, mtype))
  
  if col.comment:
    opts.append("'description' => '%s'" % col.comment)

  # Checking if is auto increment column 
  if col.autoIncrement == 1:
    type = 'serial';
  
  opts.insert(0, "'type' = '%s'" % type)
  
  if col.length > -1:
    opts.insert(1, "'length' => %d" % col.length)
  else:
    if col.scale > -1:
      opts.insert(1, "'scale' => %d" % col.scale)
    if col.precision > -1:
      opts.insert(1, "'precision' => %d" % col.precision)
  
  for f in col.flags:
    if f == 'UNSIGNED':
      opts.insert(2, "'unsigned' => TRUE")
  
  return ', '.join(opts)


def getTableSchema(table):
  """Print table specifications with drupal schema structure"""
  ret = ''
  fields, indexes, uniques, primaryKeys = [], [], [], []
  
  for column in table.columns:
    fields.append("  '%s' => array(\n        %s\n      )" % (column.name, getColumnDef(column)))
  
  for index in table.indices:
    if index.isPrimary:
      for icol in index.columns:
        primaryKeys.append("'%s'" % icol.referencedColumn.name)
    elif index.unique:
      icols = []
      for icol in index.columns:
        icols.append("'%s'" % icol.referencedColumn.name)
      uniques.append("'%s' => array(%s)" % (index.name, ', '.join(icols)))
    else:
      icols = []
      for icol in index.columns:
        icols.append("'%s'" % icol.referencedColumn.name)
      indexes.append("'%s' => array(%s)" % (index.name, ', '.join(icols)))
  
  ret += "  'fields' => array(\n    "
  ret += ",\n    ".join(fields)
  ret += "\n  ),\n"
  
  if len(indexes):
    ret += "  'indexes' => array(\n    %s\n  ),\n" % ",\n    ".join(indexes)
  if len(uniques):
    ret += "  'unique keys' => array(\n    %s\n  ),\n" % ",\n    ".join(uniques)
  if len(primaryKeys):
    ret += "  'primary key' => array(%s),\n" % ", ".join(primaryKeys)
  
  return ret

@ModuleInfo.plugin("wb.catalog.util.drupalDumpSchema", caption= "Drupal Schema Genarel - All Tables", input= [wbinputs.currentCatalog()], pluginMenu= "Catalog")
@ModuleInfo.export(grt.INT, grt.classes.db_Catalog)
def PrintDrupalSchemas(catalog):
  output = ''
  for schema in catalog.schemata:
    for table in schema.tables:
      output += "$schema['%s'] = array(\n" % table.name
      if table.comment:
        output += "  'description' => '%s',\n" % table.comment
      output += getTableSchema(table)
      output += ");\n\n"
  
  output += "return $schema;\n"
  
  c_title = 'Copy to clipboard?'
  c_message = 'The Drupal Schema can be viewed at Output Window, but if you want, you can copy to clipboard.'
  if grt.modules.Workbench.confirm(c_title, c_message):
    grt.modules.Workbench.copyToClipboard(output)
  
  print output

  return 0
