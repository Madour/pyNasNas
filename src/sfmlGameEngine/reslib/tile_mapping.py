import xml.etree.ElementTree as Et
from sfml import sf
from . import textures_loader
from ..data.game_obj import GameObject
from ..data import rect
from .resource_path import resource_path


class TilesetsLoader:
    def __init__(self):
        self.count = 0
        self.tilesets = {}

    def load_tileset(self, tileset_tag):
        t = TileSet(tileset_tag, self.count)
        #print("Loaded .tsx :", t.name)
        self.tilesets[t.name] = t
        self.count += 1
        return t

    def values(self):
        return self.tilesets.values()

    def __contains__(self, item):
        if isinstance(item, str):
            if item in self.tilesets:
                return True
            return False
        else:
            raise IndexError("Error, `in` comparison with TilesetsContainer should be a string")

    def __getitem__(self, item):
        if item in self.tilesets:
            return self.tilesets[item]
        else:
            raise IndexError(f"No item {item} in tilesets")

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self.tilesets[key] = value
        else:
            raise IndexError(f"Error, key {key} must be a string")


Tilesets_Loader = TilesetsLoader()


class TileMap(GameObject):
    def __init__(self, map_name):
        #print("--------------\n"+"---Loading map : ", map_name, "---")
        AnimatedTile.map = self
        InterractionTile.map = self

        # tmx = Et.parse(resource_path(MAPS_DIR+map_name+'.tmx'))
        tmx = Et.parse(map_name)
        root = tmx.getroot()

        self.name = map_name[:map_name.find('.')]
        self.width = int(root.attrib['width'])
        self.height = int(root.attrib['height'])

        self.tileW = int(root.attrib['tilewidth'])
        self.tileH = int(root.attrib['tileheight'])

        self.pxWidth = self.width*self.tileW
        self.pxHeight = self.height*self.tileH

        #self.tilesets = {}
        self.tiles_list = []
        self.tiles_array = {}
        self.tilesets = {}

        # collect tilesets and their information and store it in self.tilesets
        self.get_tilesets(root.findall('tileset'))
        self.vertices_dict = {}
        self.render_textures = []
        self.tile_layers_xml = root.findall('layer')
        self.object_layers_xml = root.findall('objectgroup')
        self.layers = {}
        self.animated_tiles = {}
        self.interraction_tiles = {}
        self.collisions = []
        self.collisions_shapes = []

        self.parse_map()
        #print("---Finished loading map :", map_name,"---"+"\n--------------")

    def get_tilesets(self, tilesets):
        already_loaded = False
        for tileset_tag in tilesets:
            name = tileset_tag.get('name')
            if name is not None:
                if name not in Tilesets_Loader:
                    new_tileset = Tilesets_Loader.load_tileset(tileset_tag)
                    self.tilesets[name] = {
                        'data': new_tileset,
                        'firstgid':int(tileset_tag.get('firstgid')),
                        'lastgid':int(tileset_tag.get('firstgid')) + new_tileset.tilecount-1
                    }
                else:
                    already_loaded = True
            else:
                source = tileset_tag.get('source')
                name = source[:source.find(".")]
                if name not in Tilesets_Loader:
                    new_tileset = Tilesets_Loader.load_tileset(tileset_tag)
                    self.tilesets[name] = {
                        'data': new_tileset,
                        'firstgid': int(tileset_tag.get('firstgid')),
                        'lastgid': int(tileset_tag.get('firstgid')) + new_tileset.tilecount-1
                    }
                else:
                    already_loaded = True
            if already_loaded:
                self.tilesets[name] = {
                    'data': Tilesets_Loader[name],
                    'firstgid': int(tileset_tag.get('firstgid')),
                    'lastgid': int(tileset_tag.get('firstgid')) + Tilesets_Loader[name].tilecount - 1

                }

    def parse_map(self):
        layer_index = 0
        current_tileset = None
        transformations = [0]
        for tile_layer_xml in self.tile_layers_xml:
            layer_name = tile_layer_xml.get('name')
            self.tiles_array[layer_name] = []

            self.layers[layer_name] = MapLayer(layer_name, not bool(tile_layer_xml.get('visible')))

            for props in tile_layer_xml.findall('properties'):
                for prop in props:
                    self.layers[layer_name].add_property(prop.get('name'), prop.get('value'))

            self.tiles_list = self.xml_to_list(tile_layer_xml)
            self.layers[layer_name].animated_tiles = {}
            self.animated_tiles[layer_name] = {}
            self.layers[layer_name].interraction_tiles = {}
            self.interraction_tiles[layer_name] = {}

            self.render_textures.append(self.create_render_texture())
            self.render_textures[layer_index].clear(sf.Color.TRANSPARENT)
            self.vertices_dict = {}

            for tileset in Tilesets_Loader.values():
                self.vertices_dict[tileset.id] = sf.VertexArray(sf.PrimitiveType.QUADS)
                self.vertices_dict[tileset.id].resize(self.width * self.height * 4)
            vertice_index = 0

            for j in range(self.height):
                self.tiles_array[layer_name].append([])
                for i in range(self.width):
                    self.tiles_array[layer_name][j].append(None)
                    tile_gid = self.tiles_list[i + j * self.width]
                    self.tiles_array[layer_name][j][i] = tile_gid - 1

                    if tile_gid != 0:
                        transformations = self.get_tile_transformation(tile_gid)
                        for tr in transformations:
                            tile_gid -= tr
                        for tileset in self.tilesets.values():
                            if tileset['firstgid'] <= tile_gid <= tileset['lastgid']:
                                tile_gid -= tileset['firstgid']
                                current_tileset = tileset['data']
                                break
                    else:
                        tile_gid = -1

                    if current_tileset is None:
                        current_tileset = list(self.tilesets.values())[0]['data']

                    if tile_gid in current_tileset.animations:
                        the_animated_tile = AnimatedTile(current_tileset.animations[tile_gid], i, j, current_tileset)
                        self.animated_tiles[layer_name][f"{i},{j}"] = the_animated_tile
                        self.layers[layer_name].animated_tiles[f"{i},{j}"] = the_animated_tile
                        tile_gid = -1

                    if tile_gid in current_tileset.properties:
                        if "interraction" in current_tileset.properties[tile_gid]:
                            if int(current_tileset.properties[tile_gid]["state"]) == 0:
                                the_interraction_tile = InterractionTile(tile_gid, i, j, current_tileset)
                                self.interraction_tiles[layer_name][f"{i},{j}"] = the_interraction_tile
                                self.layers[layer_name].interraction_tiles[f"{i},{j}"] = the_interraction_tile
                                tile_gid = -1

                    tx = (tile_gid % current_tileset.width) * self.tileW
                    ty = (tile_gid // current_tileset.width) * self.tileH

                    # une tile existe
                    if tile_gid >= 0:

                        self.vertices_dict[current_tileset.id][vertice_index + 0].position = sf.Vector2(i * self.tileW, j * self.tileH)
                        self.vertices_dict[current_tileset.id][vertice_index + 1].position = sf.Vector2((i + 1) * self.tileW, j * self.tileH)
                        self.vertices_dict[current_tileset.id][vertice_index + 2].position = sf.Vector2((i + 1) * self.tileW, (j + 1) * self.tileH)
                        self.vertices_dict[current_tileset.id][vertice_index + 3].position = sf.Vector2(i * self.tileW, (j + 1) * self.tileH)

                        tex_coo = self.get_tex_vertices(tx, ty, transformations)
                        self.vertices_dict[current_tileset.id][vertice_index + 0].tex_coords = tex_coo[0]
                        self.vertices_dict[current_tileset.id][vertice_index + 1].tex_coords = tex_coo[1]
                        self.vertices_dict[current_tileset.id][vertice_index + 2].tex_coords = tex_coo[2]
                        self.vertices_dict[current_tileset.id][vertice_index + 3].tex_coords = tex_coo[3]

                    # pas de tile, on remplit avec du transparent
                    else:
                        self.vertices_dict[0][vertice_index + 0].position = sf.Vector2(i * self.tileW, j * self.tileH)
                        self.vertices_dict[0][vertice_index + 1].position = sf.Vector2((i + 1) * self.tileW, j * self.tileH)
                        self.vertices_dict[0][vertice_index + 2].position = sf.Vector2((i + 1) * self.tileW, (j + 1) * self.tileH)
                        self.vertices_dict[0][vertice_index + 3].position = sf.Vector2(i * self.tileW, (j + 1) * self.tileH)

                        self.vertices_dict[0][vertice_index + 0].color = sf.Color.TRANSPARENT
                        self.vertices_dict[0][vertice_index + 1].color = sf.Color.TRANSPARENT
                        self.vertices_dict[0][vertice_index + 2].color = sf.Color.TRANSPARENT
                        self.vertices_dict[0][vertice_index + 3].color = sf.Color.TRANSPARENT

                    vertice_index += 4

            for vertice_id in self.vertices_dict:
                self.render_textures[layer_index].draw(self.vertices_dict[vertice_id],
                                                       sf.RenderStates(texture=list(Tilesets_Loader.values())[vertice_id].texture))
            self.render_textures[layer_index].display()
            self.layers[layer_name].sprite = sf.Sprite(self.render_textures[layer_index].texture)
            layer_index += 1

        for object_layer in self.object_layers_xml:
            if object_layer.get('name') == "collisions":
                self.render_textures.append(self.create_render_texture())
                self.render_textures[layer_index].clear(sf.Color.TRANSPARENT)
                self.layers["collisions"] = MapLayer("collisions", visible=True)
                for box in object_layer:
                    x, y = int(box.get('x')), int(box.get('y'))
                    width, height = int(box.get('width')), int(box.get('height'))
                    self.collisions.append(rect.Rect((x, y), (width, height)))

                    shape = sf.RectangleShape((width, height))
                    shape.position = (x, y)
                    shape.fill_color = sf.Color(200, 0, 0, 155)
                    self.collisions_shapes.append(shape)
                    self.render_textures[layer_index].draw(shape)
                self.render_textures[layer_index].display()
                self.layers["collisions"].sprite = sf.Sprite(self.render_textures[layer_index].texture)
                layer_index += 1

    def get_tile_prop(self, x, y, layer, prop_name=None):
        tile_id = self.tiles_array[layer][y][x]
        for tileset in self.tilesets.values():
            if tileset['firstgid'] <= tile_id+1 < tileset['lastgid']:
                tile_id -= tileset['firstgid']-1
                if not prop_name:
                    return tileset['data'].properties[tile_id]
                else:
                    try:
                        return tileset['data'].properties[tile_id][prop_name]
                    except KeyError:
                        print('Tileset %s: id %d has no property named %s' % (tileset.name, tile_id, prop_name))

    @staticmethod
    def get_tile_transformation(tile_gid):
        xflip = bool((tile_gid & TileTransformation.HORIZONTAL_FLIP) >> 31)
        yflip = bool((tile_gid & TileTransformation.VERTICAL_FLIP) >> 30)
        diagflip = bool((tile_gid & TileTransformation.DIAGONAL_FLIP) >> 29)
        transformations = []
        if xflip:
            transformations.append(TileTransformation.HORIZONTAL_FLIP)
        if yflip:
            transformations.append(TileTransformation.VERTICAL_FLIP)
        if diagflip:
            transformations.append(TileTransformation.DIAGONAL_FLIP)
        if not transformations:
            transformations = [0]
        return transformations

    @staticmethod
    def xml_to_list(layer):
        xml = layer.find('data').text
        return [int(n) for n in xml.split(',')]

    def create_render_texture(self):
        return sf.RenderTexture(self.width * self.tileW, self.height * self.tileH)

    def get_tex_vertices(self, tx, ty, transformations=None):
        tex_vert = [
            sf.Vector2(tx, ty),
            sf.Vector2(tx + self.tileW, ty),
            sf.Vector2(tx + self.tileW, ty + self.tileH),
            sf.Vector2(tx, ty + self.tileH)
        ]
        modifier = [
            sf.Vector2(0, 0),
            sf.Vector2(0, 0),
            sf.Vector2(0, 0),
            sf.Vector2(0, 0)
        ]
        index0, index1, index2, index3 = range(4)
        if TileTransformation.DIAGONAL_FLIP in transformations:
            index2 = 0
            index0 = 2
            tex_vert[0], tex_vert[2] = tex_vert[2], tex_vert[0]
        if TileTransformation.HORIZONTAL_FLIP in transformations:
            modifier[index0] += sf.Vector2(self.tileW, 0)
            modifier[index1] += sf.Vector2(-self.tileW, 0)
            modifier[index2] += sf.Vector2(-self.tileW, 0)
            modifier[index3] += sf.Vector2(self.tileW, 0)
        if TileTransformation.VERTICAL_FLIP in transformations:
            modifier[index0] += sf.Vector2(0, self.tileH)
            modifier[index1] += sf.Vector2(0, self.tileH)
            modifier[index2] += sf.Vector2(0, -self.tileH)
            modifier[index3] += sf.Vector2(0, -self.tileH)

        return [
            tex_vert[0] + modifier[0],
            tex_vert[1] + modifier[1],
            tex_vert[2] + modifier[2],
            tex_vert[3] + modifier[3]
        ]

class AnimatedTile(sf.Drawable):
    map = None

    def __init__(self, anim_data, i, j, tileset):
        sf.Drawable.__init__(self)
        self.tileset = tileset
        self.x = i
        self.y = j
        self.clock = sf.Clock()
        self.anim_index = 0
        self.frames = anim_data
        self.sprites = []

        for frame in self.frames:
            vertice = sf.VertexArray(sf.PrimitiveType.QUADS)
            vertice.resize(4)

            tx = (frame['id'] % tileset.width) * self.map.tileW
            ty = (frame['id'] // tileset.width) * self.map.tileH

            # une tile existe
            vertice[0].position = sf.Vector2(i * self.map.tileW, j * self.map.tileH)
            vertice[1].position = sf.Vector2((i + 1) * self.map.tileW, j * self.map.tileH)
            vertice[2].position = sf.Vector2((i + 1) * self.map.tileW, (j + 1) * self.map.tileH)
            vertice[3].position = sf.Vector2(i * self.map.tileW, (j + 1) * self.map.tileH)

            vertice[0].tex_coords = sf.Vector2(tx, ty)
            vertice[1].tex_coords = sf.Vector2(tx + self.map.tileW, ty)
            vertice[2].tex_coords = sf.Vector2(tx + self.map.tileW, ty + self.map.tileH)
            vertice[3].tex_coords = sf.Vector2(tx, ty + self.map.tileH)

            self.sprites.append(vertice)
        self.clock.restart()

    def update(self):
        if self.clock.elapsed_time.milliseconds > self.frames[self.anim_index]['duration']:
            self.anim_index += 1
            if self.anim_index > len(self.frames) - 1:
                self.anim_index = 0
            self.clock.restart()

    def draw(self, target, state):
        state.texture = self.tileset.texture
        target.draw(self.sprites[self.anim_index], state)


class InterractionTile(sf.Drawable):
    map = None

    def __init__(self, tile_gid, i, j, tileset):
        sf.Drawable.__init__(self)
        self.sprites = []
        self.x = i
        self.y = j
        self.tile_states = [tile_gid]
        self.state = 0
        self.tile_id = tile_gid
        self.tileset = tileset
        for tile_id in tileset.properties:
            if 'interraction' in tileset.properties[tile_id] and tile_id != self.tile_id:
                if tileset.properties[tile_id]["name"] == tileset.properties[self.tile_id]["name"]:
                    self.tile_states.append(tile_id)

        for gid in self.tile_states:
            vertice = sf.VertexArray(sf.PrimitiveType.QUADS)
            vertice.resize(4)

            tx = (gid % tileset.width) * self.map.tileW
            ty = (gid // tileset.width) * self.map.tileH

            # une tile existe
            vertice[0].position = sf.Vector2(i * self.map.tileW, j * self.map.tileH)
            vertice[1].position = sf.Vector2((i + 1) * self.map.tileW, j * self.map.tileH)
            vertice[2].position = sf.Vector2((i + 1) * self.map.tileW, (j + 1) * self.map.tileH)
            vertice[3].position = sf.Vector2(i * self.map.tileW, (j + 1) * self.map.tileH)

            vertice[0].tex_coords = sf.Vector2(tx, ty)
            vertice[1].tex_coords = sf.Vector2(tx + self.map.tileW, ty)
            vertice[2].tex_coords = sf.Vector2(tx + self.map.tileW, ty + self.map.tileH)
            vertice[3].tex_coords = sf.Vector2(tx, ty + self.map.tileH)

            self.sprites.append(vertice)

    def next_state(self):
        self.state += 1
        if self.state >= len(self.tile_states):
            self.state = 0

    def draw(self, target, state):
        state.texture = self.tileset.texture
        target.draw(self.sprites[self.state], state)


class MapLayer(GameObject, sf.Drawable):
    def __init__(self, name, visible=True):
        super().__init__()
        self.name = name
        self.visible = visible
        self.properties = {}
        self.animated_tiles = {}
        self.interraction_tiles = {}
        self.sprite = None

    @property
    def position(self):
        return self.sprite.position

    @property
    def y(self):
        return self.sprite.position.y

    def add_property(self, name, value):
        self.properties[name] = value

    def get_property(self, name):
        if name in self.properties:
            return self.properties[name]
        else:
            return None

    def update(self):
        for tile in self.animated_tiles.values():
            tile.update()

    def draw(self, target, states):
        if self.visible:
            target.draw(self.sprite)
            for tile in self.animated_tiles.values():
                target.draw(tile)
            for tile in self.interraction_tiles.values():
                target.draw(tile)


class TileSet:
    def __init__(self, tileset_tag, tile_id):
        # tileset externe dans un fichier tsx
        if tileset_tag.find('image') is None:
            tsx = Et.parse(resource_path("assets/" + tileset_tag.get('source')))
            root = tsx.getroot()
            self.external = True
        # tileset interne ( pas de tsx à charger)
        else:
            root = tileset_tag
            self.external = False

        self.xml = root
        self.id = tile_id

        # on récupere les attributs de la balise tileset
        self.name = root.get('name')
        self.width = int(root.find('image').get('width')) / int(root.get('tilewidth'))
        self.height = int(root.find('image').get('height')) / int(root.get('tileheight'))

        self.tilecount = int(root.get('tilecount'))

        # on récupere la source de l'image et crée la texture sfml
        self.source = root.find('image').get('source')
        path = self.source[:self.source.find('.')].split("/")

        res = textures_loader.TexturesLoader
        for dir in path:
            res = getattr(res, dir)
        self.texture = res

        self.properties = {}
        self.animations = {}

        for tile in root.findall('tile'):
            tile_id = int(tile.get('id'))
            for child in tile:
                # on récupère les propriétés
                if child.tag == 'properties':
                    if tile_id not in self.properties:
                        self.properties[tile_id] = {}
                    for prop in child:
                        self.properties[tile_id].update({prop.get('name'): prop.get('value')})
                # on récupère les animationss
                if child.tag == 'animation':
                    if tile_id not in self.animations:
                        self.animations[tile_id] = []
                    for frame in child:
                        self.animations[tile_id].append(
                            {'id': int(frame.get('tileid')), 'duration': int(frame.get('duration'))})


class TileTransformation:
    HORIZONTAL_FLIP = 0x80000000
    VERTICAL_FLIP = 0x40000000
    DIAGONAL_FLIP = 0x20000000
    ROT90 = 0xA0000000  # = DIAGONAL + X FLIPS
    ROT180 = 0xC0000000  # = X + Y FLIPS
    ROT270 = 0x60000000  # = DIAGONAL + Y FLIPS
