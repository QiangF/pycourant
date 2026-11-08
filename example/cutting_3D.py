#* parameter
tool_geometry = {
    "clearance_angle_deg": 3.0,
    # "element_size": 0.1e-3,
    "element_size": 0.05e-3,
    "height": 2e-3,
    "initial_clearance": 1e-3,       # not directly used in the simplified geometry
    "rake_angle_deg": 6.0,
    "width": 2e-3,
    "chip_thickness": 0.5e-3,
    "tooltip_clearance": 0.1e-3,
    "thickness": 0.4e-3,
}

workpiece_geometry = {
    # "element_size": 0.25e-3,
    "element_size": 0.125e-3,
    "height": 5e-3,
    "width": 20e-3,
    "thickness": 2e-3,
}

par_flt={}
par_flt['tool_velocity']=1
par_flt['engage_time']=(tool_geometry['tooltip_clearance'])/par_flt['tool_velocity']
par_flt['cut_time']=(workpiece_geometry['width']/2)/par_flt['tool_velocity']
par_flt['run_time']=par_flt['cut_time']+par_flt['engage_time']
par_flt['convection_coefficient']=500
par_flt['tool_T']=50+273.15
par_flt['tool_velocity_ramp_time']=par_flt['engage_time']/2
par_flt['tool_velocity']=1
par_flt['workpiece_T']=25+273.15
print('change work_dir')
work_dir = '/tmp/my_cache'

#* mesh
import gmsh
import os,math
import numpy as np
pgs={}
try:
    gmsh.finalize()
except:
    pass

gmsh.initialize()
gmsh.model.add("metal_cutting")
wp_w = workpiece_geometry["width"]
wp_h = workpiece_geometry["height"]
wp_es = workpiece_geometry["element_size"]
# Corner points
wp_p1 = gmsh.model.geo.addPoint(0.0, 0.0, 0.0, wp_es)
wp_p2 = gmsh.model.geo.addPoint(wp_w, 0.0, 0.0, wp_es)
wp_p3 = gmsh.model.geo.addPoint(wp_w, wp_h, 0.0, wp_es)
wp_p4 = gmsh.model.geo.addPoint(0.0, wp_h, 0.0, wp_es)
# Edges
wp_l1 = gmsh.model.geo.addLine(wp_p1, wp_p2)   # bottom
wp_l2 = gmsh.model.geo.addLine(wp_p2, wp_p3)   # right
wp_l3 = gmsh.model.geo.addLine(wp_p3, wp_p4)   # top
wp_l4 = gmsh.model.geo.addLine(wp_p4, wp_p1)   # left
# Curve loop and surface
wp_loop = gmsh.model.geo.addCurveLoop([wp_l1, wp_l2, wp_l3, wp_l4])
wp_surf = gmsh.model.geo.addPlaneSurface([wp_loop])
numElements=1
workpiece = gmsh.model.geo.extrude([(2,wp_surf),],0,0,- tool_geometry['thickness'],
                              numElements=[numElements,], heights=[1,], recombine=True)
workpiece_ymin = gmsh.model.add_physical_group(2, [workpiece[2][-1],], name="workpiece_ymin")
workpiece_surf = gmsh.model.add_physical_group(2, [workpiece[-1][-1],workpiece[-2][-1],], name="workpiece_surf")
workpiece_zfix = gmsh.model.add_physical_group(2, [wp_surf,workpiece[0][-1],], name="workpiece_zfix")
pgs['workpiece_ymin']=(2,workpiece_ymin)
pgs['workpiece_surf']=(2,workpiece_surf)
pgs['workpiece_zfix']=(2,workpiece_zfix)
pgs['workpiece']=(3, gmsh.model.addPhysicalGroup(3, [workpiece[1][1]], name="workpiece",))

tool_w = tool_geometry["width"]
tool_h = tool_geometry["height"]
tool_es = tool_geometry["element_size"]
rake_deg = tool_geometry["rake_angle_deg"]
clear_deg = tool_geometry["clearance_angle_deg"]
chip_th = tool_geometry["chip_thickness"]
rake_rad = math.radians(rake_deg)
clear_rad = math.radians(clear_deg)
# Tool tip (reference point) – upper‑left corner of the workpiece
x_tip = - tool_geometry['tooltip_clearance']
y_tip = wp_h - chip_th
# Parallelogram vertices
# 前角 (Rake Angle): 刀具的前刀面（切屑流出的平面）與垂直於工作表面的基準面之間的夾角。它決定了刀具切入材料時的「傾斜」或「銳利」程度。
# 後角 (Clearance Angle)：刀具的後刀面（與已加工表面相對的側面）與切削速度方向（或工件切線）之間的夾角。在刀具與工件之間提供一個間隙空間，避免後刀面直接摩擦已加工表面。

# P0 = tip
# P1 = end of rake face (upward‑left)
# P3 = end of flank face (downward‑left)
# P2 = fourth corner (P1 + flank vector, or P3 + rake vector)
P0 = (x_tip, y_tip)
Ref = (x_tip, y_tip + tool_w * math.cos(rake_rad))
P1 = (x_tip - tool_h * math.sin(rake_rad),
      y_tip + tool_h * math.cos(rake_rad))
P3 = (x_tip - tool_w * math.cos(clear_rad),
      y_tip + tool_w * math.sin(clear_rad))
P2 = (P1[0] - tool_w * math.cos(clear_rad),
      P1[1] + tool_w * math.sin(clear_rad))
# Create points
tpRef = gmsh.model.geo.addPoint(Ref[0], Ref[1], 0.0, tool_es)
tp0 = gmsh.model.geo.addPoint(P0[0], P0[1], 0.0, tool_es)
tp1 = gmsh.model.geo.addPoint(P1[0], P1[1], 0.0, tool_es)
tp2 = gmsh.model.geo.addPoint(P2[0], P2[1], 0.0, tool_es)
tp3 = gmsh.model.geo.addPoint(P3[0], P3[1], 0.0, tool_es)
# Create edges
t_l0 = gmsh.model.geo.addLine(tp0, tp1)   # rake face (contacting)
t_l1 = gmsh.model.geo.addLine(tp1, tp2)   # top side
t_l2 = gmsh.model.geo.addLine(tp2, tp3)   # left side
t_l3 = gmsh.model.geo.addLine(tp3, tp0)   # flank face (contacting)
# Curve loop and surface
t_loop = gmsh.model.geo.addCurveLoop([t_l0, t_l1, t_l2, t_l3])
t_surf = gmsh.model.geo.addPlaneSurface([t_loop])
tool = gmsh.model.geo.extrude([(2,t_surf),],0,0,- tool_geometry['thickness'],
                              numElements=[numElements,], heights=[1,], recombine=True)
# Tool reference point (the tip)
pg_tool_ref = gmsh.model.addPhysicalGroup(0, [tpRef], name='tooltip')
pgs['tooltip']=(0, pg_tool_ref)
# Contacting edges: rake face (t_l0) and flank face (t_l3)
# pg_contact = gmsh.model.addPhysicalGroup(2, [tool[2][1], tool[-1][1]],name="tool_surf")
pg_contact = gmsh.model.addPhysicalGroup(2, [-tool[2][1], -tool[-1][1]],name="tool_surf")
pgs['tool_surf']=(2, pg_contact)
pgs['tool']=(3, gmsh.model.addPhysicalGroup(3, [tool[1][1],],name='tool'))

gmsh.model.geo.synchronize()
# Number of nodes per edge (rounded to nearest integer)
n_wp_horiz = int(round(wp_w / wp_es)) + 1   # horizontal edges
n_wp_vert  = int(round(wp_h / wp_es)) + 1   # vertical edges
# Set transfinite curves
gmsh.model.mesh.setTransfiniteCurve(wp_l1, n_wp_horiz)
gmsh.model.mesh.setTransfiniteCurve(wp_l3, n_wp_horiz)
gmsh.model.mesh.setTransfiniteCurve(wp_l2, n_wp_vert)
gmsh.model.mesh.setTransfiniteCurve(wp_l4, n_wp_vert)
# Set transfinite surface (auto‑detect corners)
gmsh.model.mesh.setTransfiniteSurface(wp_surf)
# Recombine into quads
gmsh.model.mesh.setRecombine(2, wp_surf)
n_tool_w = int(round(tool_w / tool_es)) + 1
n_tool_h = int(round(tool_h / tool_es)) + 1
gmsh.model.mesh.setTransfiniteCurve(t_l0, n_tool_w)   # rake face
gmsh.model.mesh.setTransfiniteCurve(t_l1, n_tool_h)   # top side
gmsh.model.mesh.setTransfiniteCurve(t_l2, n_tool_w)   # left side
gmsh.model.mesh.setTransfiniteCurve(t_l3, n_tool_h)   # flank face
gmsh.model.mesh.setTransfiniteSurface(t_surf)
gmsh.model.mesh.setRecombine(2, t_surf)

gmsh.model.mesh.generate(3)
gmsh.model.mesh.renumberNodes()
gmsh.model.mesh.renumberElements()
gmsh.write(os.path.join(work_dir, "mesh.msh"))

#* starter
import os, sys
sys.path.append(os.path.dirname(os.getcwd()))
from pycourant.keyword.starter import *
starter = Starter(add_separator=False, add_header = True)
# single-layer HEX8 orthogonal cutting model
starter.add(Begin("cutting",2025))
# starter.add(Analy())

#* function
starter.add(
    Funct(
        ID =1,
        title='Constant',
        x_y = np.array([(0, 1), (10000, 1)]),
    )
)

starter.add(
    Funct(
        ID=2,
        title='Ramp',
        x_y = np.array([(0, 0), (1, 1), (10000, 1)]),
    )
)

#* material & prop
A1045 ={
    'rho_i': 7800,
    'E': 2.0e11,
    'nu': 0.3,
    'I_flag': 0,
    'a': 5.53e8,
    'b': 6.008e8,
    'n': 0.234,
    'eps_max_p': 0.0,
    'sigma_max_0': 0,
    'c': 0.0134,
    'eps_dot_0': 1,
    'ICC': 0,
    # STRAIN RATE  EFFECT HAS BEEN CONSIDERED, ACTIVATE STRAIN RATE FILTERING with Fsmooth=1 and Fcut
    # 'F_smooth': 0,
    # 'F_cut': 0,
    'C_hard': 0,
    'm': 1.0,
    'T_melt': 1460+273.15,
    'rho_C_p': 351e4,
    'T_r': 20+273.15
}

A1045_heatmat={
    'T0':20+273.15,
    'rho0_Cp': 351e4,
    'AS': 50,
    'BS': 0,
    'T1': 1460+273.15,
    'AL': 1,
    'BL': 1,
    'EFRAC': 0.9
}

starter.add(
    MatPlas_johns(ID=1, title="AISI 1045", **A1045)
)

# thermal conductivity value in `/HEAT/MAT` (should be ~6.7–23 W/(m·K)
starter.add(
    HeatMat(
        ID=1,
        T0 = A1045['T_r'],
        T1 = A1045['T_melt'],
        rho0_Cp=A1045['rho_C_p'],
        # thermal conductivity coeff
        AS = 50,
        BS = 0,
        AL = 1,
        BL = 1,
        EFRAC=0.9,
    )
)

starter.add(
    FailJohnson(
        ID = 1,
        D1 = 0.05,
        D2 = 0.35,
        D3 = -2.73,
        D4 = 0.0018,
        D5 = 0.55,
        epsilon_dot_0 = 1.0,
        Ifail_sh = 1,
        Ifail_so = 1,
        # EPSFmin = 1.2,
        EPSFmin = 0,
        Dadv = 0,
        Ixfem = 0,
        failID = 0
    )
)

# starter.add(
#     ThermStressMat
# )
starter.add(
    PropSolid(
        ID=1,
        title="Work piece prop",
        Isolid = 1,
        Ismstr = 2,
        Icpre = 0,
        Inpts = 0,
        Itetra4 = 0,
        Iframe = 0,
        dn = 0,
        qa = 0,
        qb = 0,
        h = 0.1,
        lambda_v = 0,
        mu_v = 0,
        dt_min = 0,
        Istrain = 0,
        IHKT = 0,
    )
)

#* part & node
# partID/subsetID, matID, propID
part_dict = {'workpiece':(1, 1, 1, 1), 'tool':(2, 1, 1, 2)}
for k in part_dict:
    starter.add(
        Part(
        ID = part_dict[k][0],
        title = k,
        matID = part_dict[k][1],
        propID = part_dict[k][2],
        subsetID = part_dict[k][3],
        )
    )
    starter.add(
        Subset(
        ID = part_dict[k][3],
        title = k,
        subIDs = [],
        )
    )

# nids, _ = gmsh.model.mesh.getNodesForPhysicalGroup(dim, tag)
nids, ncoords, _ = gmsh.model.mesh.get_nodes(includeBoundary = True)
ncoords = ncoords.reshape(-1, 3)
# In plane strain analysis (N2D3D =2), X is the plane strain direction, x-y plane to y-z plane
# items = np.hstack([np.array([nids, ]).transpose(), ncoords[:, [2, 0, 1]], ])
items = np.hstack([np.array([nids, ]).transpose(), ncoords, ])
items = np.unique(items, axis = 0)
starter.add(
    Node(
        ids = np.int64(items[:, 0]),
        values = items[:, (1, 2, 3)],
    )
)

#* part/element def: brick shell truss
items=np.empty([0,9],dtype=np.uint64)
for k in ['workpiece', 'tool',]:
    ids = []
    values = []
    dim = pgs[k][0]
    tag = pgs[k][1]
    for geoID in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
        _ , et_eids, et_nids = gmsh.model.mesh.getElements(dim, geoID)
        ids.extend(et_eids[0])
        values.extend(et_nids[0])
    values = np.array(np.array(values).reshape(-1, int(len(values)/len(ids))))
    values = np.hstack((np.array(ids)[:,None], values))
    items=np.vstack((items,values))

items= items[items[:,0].argsort()]
items = np.unique(items, axis = 0)

# id is partID
# 进行 2D 分析时需将单元类型从 Shell 改为 QUAD
starter.add(
    Element(
        ID = part_dict[k][0],
        dim = dim,
        # renumber element
        # items = np.hstack((np.arange(1,len(items)+1)[:,None], items[:,1:])),
        items=items,
    )
)

#* group def: grnod grshel grbrick
# surf/line def: surf/seg, line/seg
segs = {}
grnods = {}
model_dim = 3
for k in pgs:
    dim = pgs[k][0]

    nodeIDs = set()
    tag = pgs[k][1]
    ID = tag

    geoIDs = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)
    eids = []
    nids = []
    for geoID in geoIDs:
        _ , et_eids, et_nids = gmsh.model.mesh.getElements(dim, geoID)
        for i in et_nids: nodeIDs.update(i)
        if model_dim > dim > 0:
            # type(geoID) numpy.int32
            eids.append(et_eids[0])
            nids.append(et_nids[0])

    if model_dim > dim > 0:
        starter.add(
            Seg(
                dim = dim,
                ID = ID,
                title = k,
                elemIDs = np.concatenate(eids),
                nodeIDs = np.concatenate(nids),
            )
        )
        segs[k] = ID

    # node set
    starter.add(
        Gr(
            ID = ID,
            title = k,
            dim = 0,
            itemIDs = list(nodeIDs),
        )
    )
    grnods[k] = ID

#* tool (rigid body)
k = 'tooltip'
dim = pgs[k][0]
tag = pgs[k][1]
geoID = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)[0]
_ , _, nids = gmsh.model.mesh.getElements(dim, geoID)
starter.add(
    Rbody(
        ID = 1,
        title = 'tool',
        mass = 0.01, # tool mass
        nodeID = nids[0][0],
        grndID = grnods['tool'],
        surfID = 0,
    )
)

#* interaction
starter.add(
    InterType7(
        ID = 1,
        title = 'Tool rake/nose/clearance master surface',
        grndID_s = grnods['workpiece'],
        surfID_m = segs['tool_surf'],
        Istf=2,
        Ithe = 1,
        st_fac=1,
        fric = 0.3,
        gap_min = tool_geometry['element_size']/500,
        vis_f=1,
        bumult=1,
        # Rthe=1.5e4,
        Kthe = par_flt['convection_coefficient'],
        Tint = par_flt['tool_T'], # Interface temperature
        Ithe_form=1,
        fheat_s=0.5,
        fheat_m=0.5,
    )
)

#* boundary BCS
starter.add(
    Bcs(
        ID=1,
        title="workpiece bottom",
        # only layer thick, ymin is in zfix
        trarot=[1, 1, 0, 0, 0, 0],
        # trarot=[1, 1, 1, 0, 0, 0],
        skewID=0,
        grndID=grnods['workpiece_ymin'],
    )
)

starter.add(
    Bcs(
        ID=2,
        title="workpiece zfix",
        trarot=[0, 0, 1, 0, 0, 0],
        skewID=0,
        grndID=grnods['workpiece_zfix'],
    )
)

starter.add(
    Bcs(
        ID=3,
        title="tooltip (reference point)",
        # moveable in y direction
        trarot=[0, 1, 1, 1, 1, 1],
        skewID=0,
        grndID=grnods['tooltip'],
    )
)

starter.add(
    Impvel(
        ID = 1,
        title = 'Tool moving',
        grndID = grnods['tooltip'],
        fctID_t = 2,
        dir = 'X',
        Ascale_x= par_flt['tool_velocity_ramp_time'],
        Fscale_y= par_flt['tool_velocity'],
    )
)

starter.add(
    Imptemp(
        ID = 1,
        title = 'Tool temperature',
        grndID = grnods['tool'],
        fctID_t = 1,
        Fscale_y= par_flt['tool_T'],
    )
)

#* initial condition
starter.add(
    Initemp(
        ID = 1,
        title = 'initial temperature',
        grndID = grnods['workpiece'],
        T0 = par_flt['workpiece_T'],
    )
)

#* time histories request
starter.add(
    ThRbody(
        ID = 1,
        title = 'Tool rigid body force and moment history',
        varIDs = ['DEF',],
        # rigid body identifier
        objIDs = [1, ],
    )
)

#* engine
starter.add(End())
import os,glob
try:
    os.remove(os.path.join(work_dir, starter.runname + '_0000.rad'))
except:
    pass
starter.write(folder = work_dir)

from string import Template
with open('./cutting_0001.rad', 'r', encoding='utf-8') as i:
    engine_template = Template(i.read())

data = {
    "run_time": par_flt['run_time'],
    "dt_brick_f": 0.9,
    "dt_brick_min": 4E-12,
    "dt_noda_f": 0.67,
    "dt_noda_min": 0,
    "tfile_dt": par_flt['run_time']/20,
    "dt_min": par_flt['cut_time'] * 1e-7,
    # mass scaling
    "initial_mass_scaling": 10,
    "anim_dt_t0": par_flt['engage_time'],
    "anim_dt": par_flt['cut_time']/20,
}

with open(os.path.join(work_dir, starter.runname + '_0001.rad'), 'w') as i:
    i.write(engine_template.substitute(data))

#* job management
filenames = glob.glob("{}{}A*".format(work_dir, starter.runname))
for i in filenames:
    os.remove(i)

starter_command = 'starter_linux64_gf -np 1 -i {}/{}_0000.rad'.format(work_dir, starter.runname)
engine_command = 'engine_linux64_gf_ompi -nt 4 -i {}/{}_0001.rad'.format(work_dir, starter.runname)
print(starter_command)
print(engine_command)
