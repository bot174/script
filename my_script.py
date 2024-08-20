import json
from pynbt import TAG_Compound, NBTFile, TAG_Byte, TAG_Int, TAG_Short, TAG_String, TAG_List

file = 'extracted/uncensored_lib.mcstructure'

def callback():
  print('Done')

with open(file=file, mode='rb') as io:
  print('Loaded file')

  nbt = NBTFile(io=io, little_endian=True)
  print('Loaded NBT')

  block_position_data = nbt['structure']['palette']['default']['block_position_data']

  for index in block_position_data:
    print('Loading block ' + index)

    block = block_position_data[index]
    block_entity_data = block['block_entity_data']
    book = block_entity_data['book']
    written_book_content = book['components']['minecraft:written_book_content']
    author = written_book_content['author']
    pages: list[TAG_Compound] = []
    custom_name = book['components']['minecraft:custom_name']
    book_name = json.loads(custom_name)['extra'][0]['text']

    for page in written_book_content['pages']:
      raw = json.loads(page['raw'])
      text = ''.join(raw['extra'])
      page_bedrock = TAG_Compound({
        'photoname': TAG_String(''),
        'text': TAG_String(text)
      })
      pages.append(page_bedrock)
    
    new_block_entity_data = TAG_Compound({
      'book': TAG_Compound({
        'Count': TAG_Byte(1),
        'Damage': TAG_Short(0),
        'Name': TAG_String('minecraft:written_book'),
        'WasPickedUp': TAG_Byte(0),
        'tag': TAG_Compound({
          'author': TAG_String(author),
          'generation': TAG_Int(0),
          'pages': TAG_List(pages),
          'title': TAG_String('§6' + book_name),
          'xuid': TAG_String('2535453759792258')
        })
      }),
      'hasBook': TAG_Byte(1),
      'id': TAG_String('Lectern'),
      'isMovable': TAG_Byte(1),
      'page': TAG_Int(0),
      'totalPages': TAG_Int(len(pages)),
      'x': TAG_Int(block_entity_data['x']),
      'y': TAG_Int(block_entity_data['y']),
      'z': TAG_Int(block_entity_data['z'])
    })

    block['block_entity_data'] = new_block_entity_data
  
  print('Saving NBT...')
  nbt.save(callback, True)
  print('Saved NBT')