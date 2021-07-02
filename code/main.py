from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
import ezdxf
import numpy as np


def main():
    main_win = Tk()
    main_win.geometry("500x500")
    main_win.resizable(False, False)

    f1 = Frame(main_win, background="Green", width=400, height=400)
    f1.grid(row=0, column=0, sticky=NSEW)

    f1.grid_rowconfigure(0, weight=1)
    f1.grid_columnconfigure(0, weight=1)
    f1.grid_propagate(False)

    my_dpi = 72
    fig1 = Figure(figsize=(400 / my_dpi, 400 / my_dpi), dpi=my_dpi)
    ax1 = fig1.add_subplot(111)
    ax1.set_aspect('equal')
    ax1.axis('off')
    canvas1 = FigureCanvasTkAgg(fig1, master=f1)
    canvas1.get_tk_widget().grid(row=0, column=0,
                                 padx=3, pady=3,
                                 sticky=NSEW)
    f2 = Frame(f1)
    f2.grid(row=1, column=0)

    f1.grid_rowconfigure(1, weight=1)
    toolbar = NavigationToolbar2Tk(canvas1, f2)
    ax1.format_coord = lambda x, y: ""

    canvas1.draw()
    ax1.axis('off')

    coord_dict = {}

    try:
        dwg = ezdxf.readfile(r"D:\python_test\plot_draw\6o3yxyr7.dxf")
        # dwg = ezdxf.readfile(r"D:\orcad_learn\test\ttttt.dxf")
        # dwg = ezdxf.readfile(r"D:\orcad_learn\test\test_dxf.dxf")
        ver = dwg.dxfversion
        print(ver)
        msp = dwg.modelspace()

        layer_names = [layer.dxf.name for layer in dwg.layers]
        print(layer_names)

        for polyline in msp.query('LWPOLYLINE'):
            key = polyline.get_dxf_attrib('handle')
            tmp = []
            bulge_flag = False
            bulge_1st_coord = []
            for coord in polyline.get_points():
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

        for polyline in msp.query('POLYLINE'):
            key = polyline.get_dxf_attrib('handle')
            tmp = []
            bulge_flag = False
            bulge_1st_coord = []
            for coord, bulge in zip(polyline.points(), polyline.vertices()):
                tmp.append(list(coord + tuple([bulge.dxf.bulge])))
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
                if bulge.dxf.bulge != 0:
                    bulge_1st_coord = [coord[0], coord[1], bulge.dxf.bulge]
                    bulge_flag = True
            coord_dict[key] = tmp
    except IOError:
        print('Not a DXF file or a generic I/O error.')
    except ezdxf.DXFStructureError:
        print('Invalid or corrupted DXF file.')

    ax1.clear()
    ax1_p = {}

    kk = [key for key in coord_dict]
    print(kk)

    for key in coord_dict:
        pts = []
        tmp = []
        swap = 0
        bulge_len = 0
        for ptt in coord_dict[key]:
            if ptt[-1] != 0:
                swap = 1
                bulge_len = ptt[-1]
                pts.append(ptt[0:2])
            elif swap == 1:
                tmp = ptt[0:2]
                swap = 2
            elif swap == 2:
                res = bulge2pt4arc(pts[-1], tmp, bulge_len, npt=23)
                pts += res
                pts.append(tmp)
                swap = 0
                bulge_len = 0
            else:
                pts.append(ptt[0:2])
        ply1 = plt.Polygon(pts, closed=True, fill=False,
                           edgecolor='r', lw=1)
        ax1_p[key] = (ax1.add_patch(ply1))
        # break

    # ax1_p['aa'].remove()
    ax1.autoscale()
    ax1.set_aspect('equal')
    ax1.axis('off')
    canvas1.draw()

    main_win.mainloop()


def bulge2pt4arc(pt1, pt2, bulge_ratio, npt=5):
    res = []
    sig = bulge_ratio / abs(bulge_ratio)
    if abs(bulge_ratio) == 1:
        bulge_ratio = bulge_ratio
    elif 0 < bulge_ratio:
        bulge_ratio = bulge_ratio - 1
    elif bulge_ratio < 0:
        bulge_ratio = bulge_ratio + 1

    mp = [(pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2]
    radius = np.sqrt((pt1[0] - pt2[0]) ** 2 +
                     (pt1[1] - pt2[1]) ** 2) / 2
    angle = np.arctan2(pt2[1] - mp[1],
                       pt2[0] - mp[0]) + np.pi / 2
    cx = mp[0] - radius * np.cos(angle) * bulge_ratio
    cy = mp[1] - radius * np.sin(angle) * bulge_ratio
    cc = [cx, cy]
    radius = np.sqrt((pt1[0] - cc[0]) ** 2 +
                     (pt1[1] - cc[1]) ** 2)
    a0 = np.arctan2(pt1[1] - cc[1], pt1[0] - cc[0])
    a1 = np.arctan2(pt2[1] - cc[1], pt2[0] - cc[0])
    aa = (a1 - a0)
    aa = aa + np.pi * 2 if aa < 0 else aa

    if sig > 0:
        delta = aa / (npt + 1)
    else:
        delta = (np.pi * 2 - aa) / (npt + 1)

    for i in range(1, npt):
        aa = a0 + delta * i * sig
        cx = cc[0] + radius * np.cos(aa)
        cy = cc[1] + radius * np.sin(aa)
        res.append([cx, cy])
    return res


if __name__ == '__main__':
    main()
