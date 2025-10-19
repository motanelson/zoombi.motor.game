#pip install PyOpenGL PyOpenGL_accelerate
# board3d_skeleton.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import sys

GRID_SIZE = 16
CELL = 1.0
CAM_DISTANCE = 22.0

window_width = 900
window_height = 700

user_x = 0
user_y = 0
board = None
skeleton_tex = None

def loads(files):
    ll=True
    a=[]
    with open(files,"r") as f1:
        ttt=f1.read()
    yyy=ttt.split("\n")
    yi=len(yyy)
    for y in range(yi):
        xxx=yyy[y].split(",")
        xi=len(xxx)
        if ll:
            a=[[" " for _ in range(xi)] for __ in range(yi)]
        ll=False
        for x in range(xi):
            b=xxx[x].strip()
            a[y][x]=b if b!="" else " "
    return a

def world_pos_from_index(ix, iy):
    half = (GRID_SIZE - 1) * CELL / 2.0
    wx = ix * CELL - half
    wz = iy * CELL - half
    return wx, wz

def load_texture(filename):
    img = Image.open(filename).convert("RGBA")
    img_data = img.tobytes("raw", "RGBA", 0, -1)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    return tex_id

def init_gl():
    glClearColor(1.0, 1.0, 0.1, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_NORMALIZE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])

def draw_grid():
    glDisable(GL_LIGHTING)
    half = (GRID_SIZE - 1) * CELL / 2.0
    glBegin(GL_QUADS)
    for iy in range(GRID_SIZE):
        for ix in range(GRID_SIZE):
            wx = -half + ix * CELL
            wz = -half + iy * CELL
            if (ix + iy) % 2 == 0:
                glColor3f(0.85, 0.85, 0.1)
            else:
                glColor3f(0.65, 0.65, 0.65)
            glVertex3f(wx, 0.0, wz)
            glVertex3f(wx + CELL, 0.0, wz)
            glVertex3f(wx + CELL, 0.0, wz + CELL)
            glVertex3f(wx, 0.0, wz + CELL)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_sprite(wx, wz, tex_id, size=1.0):
    glPushMatrix()
    glTranslatef(wx, size * 0.5, wz)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    # plano de frente para a câmara
    glTexCoord2f(0, 0); glVertex3f(-size/2, 0.0, 0.0)
    glTexCoord2f(1, 0); glVertex3f(size/2, 0.0, 0.0)
    glTexCoord2f(1, 1); glVertex3f(size/2, size, 0.0)
    glTexCoord2f(0, 1); glVertex3f(-size/2, size, 0.0)
    glEnd()
    glPopMatrix()

def draw_board_skeletons():
    for iy in range(min(GRID_SIZE, len(board))):
        row = board[iy]
        for ix in range(min(GRID_SIZE, len(row))):
            if str(row[ix]).strip() != "":
                wx, wz = world_pos_from_index(ix, iy)
                draw_sprite(wx, wz, skeleton_tex, size=1.3)

def draw_user_skeleton():
    wx, wz = world_pos_from_index(user_x, user_y)
    draw_sprite(wx, wz, skeleton_tex, size=1.6)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0.0, CAM_DISTANCE * 0.5, CAM_DISTANCE,
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    glTranslatef(0.0, -5.0, 0.0)
    draw_grid()
    draw_board_skeletons()
    draw_user_skeleton()
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(w)/float(h if h > 0 else 1), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def special_key(key, x, y):
    global user_x, user_y
    if key == GLUT_KEY_LEFT:
        user_x = max(0, user_x - 1)
    elif key == GLUT_KEY_RIGHT:
        user_x = min(GRID_SIZE - 1, user_x + 1)
    elif key == GLUT_KEY_UP:
        user_y = max(0, user_y - 1)
    elif key == GLUT_KEY_DOWN:
        user_y = min(GRID_SIZE - 1, user_y + 1)
    glutPostRedisplay()

def keyboard(key, x, y):
    if key == b'\x1b' or key == b'q':
        sys.exit(0)

def main():
    global board, skeleton_tex
    try:
        board = loads("xy.csv")
    except:
        board = [[" " for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Tabuleiro 3D com Caveiras")
    init_gl()
    skeleton_tex = load_texture("zoombi.png")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutSpecialFunc(special_key)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(glutPostRedisplay)
    glutMainLoop()

if __name__ == "__main__":
    main()
