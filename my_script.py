import json
from pynbt import TAG_Compound, NBTFile, TAG_Byte, TAG_Int, TAG_Short, TAG_String, TAG_List

file = 'extracted/uncensored_lib.mcstructure'
out_file = 'extracted/out.mcstructure'

def write(nbt: NBTFile):
  print('Saving NBT...')
    
  with open(file=out_file, mode='wb') as io:
    def write_callback(data: bytes):
      io.write(data)

    nbt.save(write_callback, True)

  print('Saved NBT')

with open(file=file, mode='rb') as io:
  print('Loaded file')

  nbt = NBTFile(io=io, little_endian=True)
  io = None ## Free memory
  print('Loaded NBT')

  block_position_data = nbt['structure']['palette']['default']['block_position_data']
  new_block_position_data = {}

  for index in block_position_data:
    print('Loading block ' + index)

    block = block_position_data[index]
    block_entity_data = block['block_entity_data']
    
    if 'id' in block_entity_data and block_entity_data['id'].value == 'Lectern':
      book = block_entity_data['book']
      written_book_content = book['components']['minecraft:written_book_content']
      author = written_book_content['author'].value
      pages = TAG_List(tag_type=TAG_Compound)

      if 'minecraft:custom_name' in book['components']:
        custom_name = book['components']['minecraft:custom_name'].value
        book_name = '§6' + json.loads(custom_name)['extra'][0]['text']
      else:
        book_name = written_book_content['title']['raw'].value

      for page in written_book_content['pages']:
        raw = json.loads(page['raw'].value)
        extra: list[str] = raw['extra']
        text = ''

        for item in extra:
          if (type(item) == str):
            text += item
          else:
            text += item['text']

        page_bedrock = TAG_Compound({
          'photoname': TAG_String(''),
          'text': TAG_String(text)
        })
        pages.append(page_bedrock)
      
      new_block_entity_data = {
        'book': TAG_Compound({
          'Count': TAG_Byte(1),
          'Damage': TAG_Short(0),
          'Name': TAG_String('minecraft:written_book'),
          'WasPickedUp': TAG_Byte(0),
          'tag': TAG_Compound({
            'author': TAG_String(author),
            'generation': TAG_Int(0),
            'pages': pages,
            'title': TAG_String(book_name),
            'xuid': TAG_String('2535453759792258')
          })
        }),
        'hasBook': TAG_Byte(1),
        'id': TAG_String('Lectern'),
        'isMovable': TAG_Byte(1),
        'page': TAG_Int(0),
        'totalPages': TAG_Int(len(pages)),
        'x': TAG_Int(block_entity_data['x'].value),
        'y': TAG_Int(block_entity_data['y'].value),
        'z': TAG_Int(block_entity_data['z'].value)
      }

      new_block_position_data[index] = TAG_Compound({
        'block_entity_data': TAG_Compound(new_block_entity_data)
      })
    else:
      new_block_position_data[index] = block_entity_data

  value = {
    'format_version': TAG_Int(1),
    'size': TAG_List(TAG_Int, nbt['size'].value),
    'structure': TAG_Compound({
      'block_indices': TAG_List(TAG_List, nbt['structure']['block_indices'].value),
      'entities': TAG_List(TAG_Compound, nbt['structure']['entities'].value),
      'palette': TAG_Compound({
        "default": TAG_Compound({
          "block_palette": TAG_List(TAG_Compound, nbt['structure']['palette']['default']['block_palette'].value),
          "block_position_data": TAG_Compound(new_block_position_data),
        })
      }),
    }),
    'structure_world_origin': TAG_List(TAG_Int, nbt['structure_world_origin'].value)
  }

  write(NBTFile(value=value, little_endian=True))