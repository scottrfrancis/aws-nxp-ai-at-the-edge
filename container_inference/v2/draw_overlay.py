import cairo

def print_inference(context,inference_time):
        FONT_SIZE=10
        inf_time_str = "Inference Time " + "{:.2f}".format(inference_time)

        context.set_line_width(1)
        context.set_source_rgb(1, 0, 0)
        context.rectangle(0,0,len(inf_time_str)*6, FONT_SIZE+2)
        context.fill_preserve()
        context.set_source_rgb(1, 0, 0)
        context.stroke()

        context.select_font_face('Courier', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        context.set_font_size(FONT_SIZE)
        context.move_to(0,FONT_SIZE+2)
        context.text_path(inf_time_str)
        context.set_source_rgb(1, 1, 1)
        context.fill_preserve()
        context.set_source_rgb(1, 1, 1)
        context.set_line_width(1)
        context.stroke()

def draw_bb(context,xmin,xmax,ymin,ymax,object_index):
    class_names =['shell','elbow','penne','tortellini', 'farfalle']
    FONT_SIZE=10

    #print(xmin,xmax,ymin,ymax,class_names[object_index])

    context.set_line_width(1)
    context.set_source_rgb(0, 1, 0)
    context.rectangle(xmin, ymin,len(class_names[object_index])*6, FONT_SIZE+2)
    context.fill_preserve()
    context.set_source_rgb(0, 1, 0)
    context.stroke()

    context.set_line_width(3)
    context.set_source_rgb(0, 1, 0)
    context.set_line_join(cairo.LINE_JOIN_ROUND)
    #context.rectangle(x_rect, y_rect, width, height)
    context.rectangle(xmin, ymin,(xmax-xmin),(ymax-ymin))
    context.stroke()

    context.select_font_face('Courier', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(FONT_SIZE)
    context.move_to(xmin, ymin+FONT_SIZE)
    context.text_path(class_names[object_index])
    context.set_source_rgb(0, 0, 0)
    context.fill_preserve()
    context.set_source_rgb(0, 0, 0)
    context.set_line_width(1)
    context.stroke()
