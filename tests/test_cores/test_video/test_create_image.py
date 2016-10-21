
from random import randint
from rhea.models.video import VideoDisplay


def test_create_save():
    num_frames = 3
    resolution = res = (randint(32, 800), randint(32, 800),)
    color_depth = cd = (8, 8, 8)
    disp = VideoDisplay(resolution=resolution,
                        color_depth=color_depth)
    print(str(disp))
    for ii in range(num_frames):      
        for row in range(res[1]):
            for col in range(res[0]):
                rgb = (randint(0, cd[0]-1), 
                       randint(0, cd[1]-1), 
                       randint(0, cd[2]-1))
                last = (row == res[1]-1 and col == res[0]-1)
                if last:
                    print("End of frame {}, {}, {}".format(row, col, rgb))
                disp.set_pixel(col, row, rgb, last)
                
                
if __name__ == '__main__':
    test_create_save()
