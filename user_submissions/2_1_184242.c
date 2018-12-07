 #include<iostream.h>
 #include<stdio.h>
 #include<conio.h>
 #include<stdlib.h>
 #include<graphics.h>
 #include<dos.h>
 #include<string.h>
 #include "C:\TC\PROGRAMS\INITIALI.H"

 typedef struct line{
	int start_x, start_y, end_x, end_y;
	// Array to store code for ABRL(Above, Below, Left, Right)
	int rel_pos1[4], rel_pos2[4];
 }LINE;

 typedef struct window{
	int xcoord, ycoord;
 }WINDOW;

 void setPrompt(char *s);
 void hidePrompt();

 class CLIP{
	LINE lineObject[30];
	WINDOW win[4];
	int line_num;    // Last line index + 1

	public:
		CLIP()
		{
			line_num=0;
		}
		void accept_lines();
		void accept_window();
		void draw_clipped();
		void set_code(LINE &l);
 };


 int prompt_len=0;
 char *prompt;

 int main()
 {
	int default_color;
	clrscr();
	initGraphics();
	default_color = getcolor();
	setcolor(GREEN);
	outtextxy(getmaxx()/3 + 50,10,"Line Clipping Program");
	setcolor(default_color);
	setPrompt("Draw lines using left mouse. Use right mouse to stop.");
	CLIP c;
	c.accept_lines();
	hidePrompt();
	setPrompt("Set bottom left and top right corner of window.");
	c.accept_window();
	hidePrompt();
	setPrompt("Press any key to clip!");
	getch();
	cleardevice();
	setPrompt("Clipped lines: ");
	getch();
	c.draw_clipped();
	getch();
	closegraph();
	return 0;
 }

 void setPrompt(char *s)
 {
    prompt_len = strlen(s);
    prompt = (char*)malloc(sizeof(char) * (prompt_len+1));
    memcpy(prompt,s,prompt_len+1);
    outtextxy(10,50,prompt);
 }

 void hidePrompt()
 {
	int def_color = getcolor();
	setcolor(BLACK);
	outtextxy(10,50,prompt);
	setcolor(def_color);
	free(prompt);
	prompt_len = 0;
 }


  void CLIP::accept_lines()
 {
	int i = 0, button=0, x, y, prev_color = getcolor();
	setcolor(CYAN);
	initMouse();
	showMouse();
	while(button != 2) {
	      button = 0;
	      while(button != 1 && button != 2)
		getMousePos(&button,&x,&y);
	      if(button == 1){
		if(i % 2 == 1) {	//draw a line
			lineObject[line_num].end_x = x;
			lineObject[line_num].end_y = y;
			line(lineObject[line_num].start_x,lineObject[line_num].start_y,lineObject[line_num].end_x,lineObject[line_num].end_y);
			line_num++;
		}
		else{
			lineObject[line_num].start_x = x;
			lineObject[line_num].start_y = y;
		}
		i++;
		delay(250);
	      }
	}
	setcolor(prev_color);
	hideMouse();
 }
// Below = 1, Left = 2->3, Above = 0, Right = 3->2
 void CLIP::accept_window()
 {
	int button=0, x, y;
	initMouse();
	showMouse();
	while(button != 1)
		getMousePos(&button,&x,&y);
	delay(500);
	win[1].ycoord = y; win[3].xcoord = x;
	button=0;
	while(button != 1)
		getMousePos(&button,&x,&y);
	win[0].ycoord = y;
	win[2].xcoord = x;
	int def_color = getcolor();
	setcolor(RED);
	// Bottom win
	line(win[3].xcoord,win[1].ycoord,win[2].xcoord,win[1].ycoord);
	delay(500);
	// Right
	line(win[2].xcoord,win[1].ycoord,win[2].xcoord,win[0].ycoord);
	delay(500);
	//Top
	line(win[3].xcoord,win[0].ycoord,win[2].xcoord,win[0].ycoord);
	delay(500);
	//Left
	line(win[3].xcoord,win[0].ycoord,win[3].xcoord,win[1].ycoord);
	delay(500);
	setcolor(def_color);
	hideMouse();
 }

 // Cohen-Sutherland line clip algorithm
 void CLIP::draw_clipped()
 {
	int def_color = getcolor(), lines_inside_window=0;
    while(lines_inside_window < line_num){
	cleardevice();
	for(int i = 0; i < line_num; ++i){
		set_code(lineObject[i]);
		// If completely visible
		int j;
		for(j = 0; j < 4; ++j) {
			if(lineObject[i].rel_pos1[j] == lineObject[i].rel_pos2[j] && lineObject[i].rel_pos1[j] == 0)
				;
			else
				break;
		}
		if(j == 4){
			lines_inside_window++;
			continue;
		}
		else{
			// if completely invisible
			int k;
			for(k = 0; k < 4; ++k){
				if(lineObject[i].rel_pos1[k] == lineObject[i].rel_pos2[k] && lineObject[i].rel_pos1[k] == 1)
					break;
			}
			if(k < 4){
				lineObject[i].start_x = -1; //dont draw the line
				continue;
			}
			else {
				// Need to add handline of infinity
				double slope = (double)(lineObject[i].end_y - lineObject[i].start_y)/(double)(lineObject[i].end_x - lineObject[i].start_x);
				// Check the side does the start lies
				for(int t1 = 0; t1 < 4; ++t1)
					if(lineObject[i].rel_pos1[t1] == 1)
						break;
				if(t1 < 4){
					switch(t1){
						case 0:	//above
						{
							lineObject[i].start_x += ((win[t1].ycoord - lineObject[i].start_y)/slope);
							lineObject[i].start_y = win[t1].ycoord;
						}
						break;

						case 1:	//below
						{
							lineObject[i].start_x += ((win[t1].ycoord - lineObject[i].start_y)/slope);
							lineObject[i].start_y = win[t1].ycoord;
						}
						break;

						case 2: //right
						{
							lineObject[i].start_y += (slope * (win[t1].xcoord - lineObject[i].start_x));
							lineObject[i].start_x = win[t1].xcoord;
						}
						break;

						case 3: //left
						{
							lineObject[i].start_y += (slope * (win[t1].xcoord - lineObject[i].start_x));
							lineObject[i].start_x = win[t1].xcoord;
						}
						break;
					}
				}

				for(int t2 = 0; t2 < 4; ++t2)
					if(lineObject[i].rel_pos2[t2] == 1)
						break;
				if(t2 < 4){
					switch(t2){
						case 0:	//above
						{
							lineObject[i].end_x += ((win[t2].ycoord - lineObject[i].end_y)/slope);
							lineObject[i].end_y = win[t2].ycoord;
						}
						break;
						case 1:	//below
						{
							lineObject[i].end_x += ((win[t2].ycoord - lineObject[i].end_y)/slope);
							lineObject[i].end_y = win[t2].ycoord;
						}
						break;

						case 2: //right
						{
							lineObject[i].end_y += (slope * (win[t2].xcoord - lineObject[i].end_x));
							lineObject[i].end_x = win[t2].xcoord;
						}
						break;

						case 3: //left
						{
							lineObject[i].end_y += (slope * (win[t2].xcoord - lineObject[i].end_x));
							lineObject[i].end_x = win[t2].xcoord;
						}
						break;
					}
				}
			}
		}
	}

     }

	// Draw clipped lines
	setcolor(CYAN);
	for(int i = 0; i < line_num; ++i){
		if(lineObject[i].start_x != -1){
			line(lineObject[i].start_x, lineObject[i].start_y, lineObject[i].end_x, lineObject[i].end_y);
		}
	}
	//draw window
	setcolor(RED);
	// Bottom win
	line(win[3].xcoord,win[1].ycoord,win[2].xcoord,win[1].ycoord);
	delay(500);
	// Right
	line(win[2].xcoord,win[1].ycoord,win[2].xcoord,win[0].ycoord);
	delay(500);
	//Top
	line(win[3].xcoord,win[0].ycoord,win[2].xcoord,win[0].ycoord);
	delay(500);
	//Left
	line(win[3].xcoord,win[0].ycoord,win[3].xcoord,win[1].ycoord);
	delay(500);
	setcolor(def_color);
	hideMouse();

 }

 // set ABRL opcode for each point of a line
 void CLIP::set_code(LINE &l)
 {
	if(l.start_y < win[0].ycoord)
		l.rel_pos1[0] = 1;
	else
		l.rel_pos1[0] = 0;
	if(l.end_y < win[0].ycoord)
		l.rel_pos2[0] = 1;
	else
		l.rel_pos2[0] = 0;
	if(l.start_y > win[1].ycoord)
		l.rel_pos1[1] = 1;
	else
		l.rel_pos1[1] = 0;
	if(l.end_y > win[1].ycoord)
		l.rel_pos2[1] = 1;
	else
		l.rel_pos2[1] = 0;
	if(l.start_x > win[2].xcoord)
		l.rel_pos1[2] = 1;
	else
		l.rel_pos1[2] = 0;
	if(l.end_x > win[2].xcoord)
		l.rel_pos2[2] = 1;
	else
		l.rel_pos2[2] = 0;
	if(l.start_x < win[3].xcoord)
		l.rel_pos1[3] = 1;
	else
		l.rel_pos1[3] = 0;
	if(l.end_x < win[3].xcoord)
		l.rel_pos2[3] = 1;
	else
		l.rel_pos2[3] = 0;
 }
