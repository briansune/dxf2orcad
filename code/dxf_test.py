import ezdxf
import sys
from pprint import pprint
import numpy as np

coord_dict = {}

try:
    dwg = ezdxf.readfile(r"D:\orcad_learn\test\ttttt.dxf")
    # dwg = ezdxf.readfile(r"D:\orcad_learn\test\test_dxf.dxf")
    ver = dwg.dxfversion
    print(ver)
    msp = dwg.modelspace()

    layer_names = [layer.dxf.name for layer in dwg.layers]
    print(layer_names)

    plyll_n = list(msp.query('LWPOLYLINE'))
    plyll_o = list(msp.query('POLYLINE'))
    if plyll_n:
        plyll = plyll_n
    elif plyll_o:
        plyll = plyll_o
    else:
        plyll = []

    for polyline in plyll:
        key = polyline.get_dxf_attrib('handle')
        tmp = []
        bulge_flag = False
        bulge_1st_coord = []

        try:
            points_list = polyline.get_points()
        except AttributeError:
            points_list = []
            for d1, d2 in zip(polyline.points(), polyline.vertices()):
                points_list.append(list(d1 + tuple([d2.dxf.bulge])))

        for coord in points_list:
            tmp.append([coord[0], coord[1], coord[-1]])
            if bulge_flag:
                bulge_flag = False
                mid_pt = [(bulge_1st_coord[0] + coord[0]) / 2,
                          (bulge_1st_coord[1] + coord[1]) / 2]
                radius = np.sqrt((coord[0] - bulge_1st_coord[0]) ** 2 +
                                 (coord[1] - bulge_1st_coord[1]) ** 2) / 2
                angle = np.arctan2(coord[1] - mid_pt[1],
                                   coord[0] - mid_pt[0]) + np.pi / 2
                cx = mid_pt[0] - radius * np.cos(angle) * bulge_1st_coord[-1]
                cy = mid_pt[1] - radius * np.sin(angle) * bulge_1st_coord[-1]
                tmp.append([cx, cy, 0.0])
            if coord[-1] != 0:
                bulge_1st_coord = [coord[0], coord[1], coord[-1]]
                bulge_flag = True
        coord_dict[key] = tmp

    pprint(coord_dict)
    orccad_txt_hdr = """
version 17.4"""
    orcad_shape = """
setwindow pcb
generaledit
shape add 
setwindow form.mini
FORM mini dyns_lock_mode Line 
FORM mini class ETCH 
FORM mini dyns_fill_type 'Static solid' 
setwindow form.mini
FORM mini dyns_grid 'Current grid' 
FORM mini dyns_grid None 
setwindow pcb"""
    for k in coord_dict:
        coord_l = coord_dict[k]
        orccad_txt_hdr += orcad_shape
        for coord in coord_l:
            orccad_txt_hdr += """
pick grid {} {}""".format(coord[0], coord[1])
            if coord[-1] != 0.0:
                orccad_txt_hdr += """
setwindow form.mini
FORM mini dyns_lock_mode Arc
setwindow pcb"""
        orccad_txt_hdr += """
done 
generaledit 
"""

    with open(r'D:\orcad_learn\test\asdsadas.scr', 'w+') as wr:
        wr.write(orccad_txt_hdr)


except IOError:
    print('Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print('Invalid or corrupted DXF file.')
    sys.exit(2)
