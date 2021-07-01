from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
    canvas1 = FigureCanvasTkAgg(fig1, master=main_win)
    canvas1.get_tk_widget().grid(row=0, column=0,
                                 padx=3, pady=3,
                                 sticky=NSEW)

    canvas1.draw()
    ax1.axis('off')

    coord_dict = {}

    try:
        dwg = ezdxf.readfile(r"D:\orcad_learn\test\ttttt.dxf")
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
    for key in coord_dict:
        pts = []
        tmp = []
        swap = 0
        for ptt in coord_dict[key]:
            # print(ptt)
            if ptt[-1] != 0:
                swap = 1
                pts.append(ptt[0:2])
            elif swap == 1:
                tmp = ptt[0:2]
                swap = 2
            elif swap == 2:
                pts.append(ptt[0:2])
                pts.append(tmp)
                swap = 0
            else:
                pts.append(ptt[0:2])

        ply1 = plt.Polygon(pts, closed=True, fill=False, edgecolor='r', lw=1)
        ax1_p[key] = (ax1.add_patch(ply1))

    print(ax1_p)
    # ax1_p['aa'].remove()
    ax1.autoscale()
    ax1.set_aspect('equal')
    ax1.axis('off')
    canvas1.draw()

    main_win.mainloop()


if __name__ == '__main__':
    main()
