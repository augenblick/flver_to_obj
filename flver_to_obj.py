import struct
import binascii

# accepts a file and spits out a tuple with the top_header info (first 96 bytes)


def header_parse(filename):
    top_fmt = "5sxsxHHIIIIIIIffffffIIIIIIII"
    head_length = struct.calcsize(top_fmt)

    with open(filename, 'rb') as flver_file:
        top_data = struct.unpack(top_fmt, flver_file.read(head_length))

    return top_data


# receives number of materials and returns offset of material names and paths
def get_mat_info(mat_num):
    mat_fmt = ('IIIII12x')
    mat_info = []
    count = 0
    with open(filename, 'rb') as flver_file:
        flver_file.seek(127)
        while count < mat_num:

            mat_info.append(struct.unpack(mat_fmt, flver_file.read(32)))
            count = count + 1

    return mat_info


# receives offset and number of face sets.  returns offset and size of said sets.
def get_faceSet_info(offset, faceSet_num):
    faceSet_fmt = ('12xII12x')
    faceSet_info = []
    count = 0
    with open(filename, 'rb') as flver_file:
        flver_file.seek(offset)
        while count < faceSet_num:
            faceSet_info.append(struct.unpack(faceSet_fmt, flver_file.read(32)))
            count = count + 1
        return faceSet_info


# given the faceset_info, will return a faceSet
# called by get_faces()
def get_faceSet(offset, face_length):
    face_fmt = ('HHH')
    fmt_length = struct.calcsize(face_fmt)
    faces = []
    face_end = face_length / fmt_length
    count = 0
    with open(filename, 'rb') as flver_file:
        # print(offset)
        flver_file.seek(offset)
        while count < face_end - 1:
            faces.append(struct.unpack(face_fmt, flver_file.read(fmt_length)))
            count = count + 1
        return faces


def get_faces(faceSet_info):
    faces = []
    c = 0
    for i in faceSet_info:

        faceTemp = get_faceSet((faceSet_info[c][0] + datastart), faceSet_info[c][1])
        for i in faceTemp:
            for j in i:
                # print(j)
                faces.append(j)
        c = c + 1
    print(c)
    return faces


# receives offset of and number of vertex info and returns offset and size of vertex data
def get_vert_info(offset, mesh_num):
    vert_info_fmt = ('24xII')
    vert_info = []
    count = 0
    with open(filename, 'rb') as flver_file:
        flver_file.seek(offset)
        while count < mesh_num:
            vert_info.append(struct.unpack(vert_info_fmt, flver_file.read(32)))
            count = count + 1
        return vert_info


# given offset and size of vertices data, returns a list containing the vertex data itself
# this method is called upon by the get_meshes() function
def get_verts(offset, mesh_length):
    vert_fmt = ('fffbbbbBBBBBBBbbbbHH')
    fmt_length = struct.calcsize(vert_fmt)  # 32
    verts = []
    vert_end = mesh_length / fmt_length
    count = 0
    with open(filename, 'rb') as flver_file:
        # print(offset)
        flver_file.seek(offset)
        while count < vert_end:
            vertArray = []
            vertTuple = (struct.unpack(vert_fmt, flver_file.read(fmt_length)))
            for x in vertTuple:
                vertArray.append(x)
            verts.append(vertArray)
            count = count + 1

    # convert uv coordinates
    # umax = verts[0][18]
    # vmax = verts[0][19]
    # for i in verts:
    #     i[18] = i[18] / umax
    #     i[19] = i[19] / vmax

    for i in verts:
        u = i[18]
        if u > 32767:
            u = -(65536 - u)
        v = i[19]
        if v > 32767:
            v = -(65536 - v)
        u = abs(u / (25 * 1024))
        v = abs(v / (25 * 1024))

        uf = struct.pack('f', u / 1024)
        vf = struct.pack('f', v / 1024)

        i[18] = float('%.4f' % u)  # str(binascii.hexlify(uf)).split('\'')[1]
        i[19] = float('%.4f' % v)  # str(binascii.hexlify(vf)).split('\'')[1]

    #

    return verts

# given the vert_info, returns a list containing all vertex groups from the file


def get_meshes(vert_info):
    meshes = []
    c = 0
    for i in vert_info:
        meshes.append(get_verts((vert_info[c][1] + datastart), vert_info[c][0]))
        c = c + 1
    # print(c)
    return meshes


filename = 'm2090B0A17.flver'
# filename = 'm9000B0A17.flver'
# filename = 'D:/Unpacked DS files/map/m17_00_00_00/m2022B0A17.flver'
#filename = 'D:/Unpacked DS files/map/m13_01_00_00/m0080B1A13.flver'
top_data = header_parse(filename)

datastart = top_data[4]
datasize = top_data[5]
hbox_num = top_data[6]
mat_num = top_data[7]
bone_num = top_data[8]
mesh_num = top_data[9]
vert_info = top_data[10]
faceSet_num = top_data[21]
vert_descript = top_data[22]
mat_param = top_data[23]

faceSet_info_offset = 118 + (mat_num * 32) + (bone_num * 138) + (mat_num * 48)
vert_info_offset = faceSet_info_offset + (faceSet_num * 32)


# print(mesh_num)

mat_info = get_mat_info(mat_num)
faceSet_info = get_faceSet_info(faceSet_info_offset, faceSet_num)
vert_info = get_vert_info(vert_info_offset, mesh_num)
meshes = get_meshes(vert_info)

print(faceSet_num)
print("-->", vert_info_offset)
print((vert_info[0][1]) + datastart)

# get_faceSet((datastart + faceSet_info[2][0]), faceSet_info[2][1])
faces = get_faces(faceSet_info)


count = 1
for i in meshes:

    objname = "test"
    objname = objname + str(count) + ".obj"
    count = count + 1
    print(objname)
    with open(objname, 'w') as obj_file:
        for j in i:
            print("v", float('%.4f' % j[0]), float('%.4f' % j[1]), float('%.4f' % j[2]), file=obj_file)

        print("\n", file=obj_file)
        for j in i:
            print("vt", j[18], j[19], file=obj_file)

        print("\n", file=obj_file)
        for j in i:
            print("vn", j[7] / 255, j[8] / 255, j[9] / 255, file=obj_file)

# this is meant to reorder the faces to match the .obj format


def Faces(faces):
    faceslist = []
    StartDirection = -1
    f1 = faces[0]
    f2 = faces[1]
    FaceDirection = StartDirection
    counter = 2
    print(len(faces))
    while counter < len(faces) - 1:

        f3 = faces[counter]
        #print(f1, f2, f3)
        FaceDirection *= -1
        if (f1 != f2) and (f2 != f3) and (f3 != f1):
            if FaceDirection > 0:
                #print(f1, f2, f3)
                faceslist.append(f1)
                faceslist.append(f2)
                faceslist.append(f3)
            else:
                #print(f1, f3, f2)
                faceslist.append(f1)
                faceslist.append(f3)
                faceslist.append(f2)
        counter = counter + 1
        f1 = f2
        f2 = f3

    return faceslist


faceslist = Faces(faces)

# writes the faces to the .obj file
with open('test1.obj', 'a') as obj_file:
    print("\n", file=obj_file)
    count = 0
    while count < len(faceslist):
        # print(faceslist[1])
        print("f", faceslist[count] + 1, faceslist[count + 1] + 1, faceslist[count + 2] + 1, file=obj_file)
        count = count + 3

# print(datastart)
# print(mat_info)
# print(faceSet_info)
# print(vert_info)
# print(meshes)

# struct_fmt = "=hhh"
# struct_unpack = struct.Struct(struct_fmt).unpack_from

# with open("m2090B0A17.flver", 'rb') as flver_binary:
#     flver_binary.seek(1568)
#     counter = 0
#     while counter < 1000:
#         data = flver_binary.read(6)
#         if not data:
#             break
#         s = struct_unpack(data)
#         print(counter, end="")
#         print(s)
#         counter = counter + 1
