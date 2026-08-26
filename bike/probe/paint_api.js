function paint() {
  brush.noField();

  // 1 filled polygon with bleeding edge
  brush.fill('#e0553a', 80);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([[-320,-260],[-170,-260],[-170,-130],[-320,-130]]);
  brush.noFill();

  // 2 filled circle
  brush.fill('#3a7de0', 70);
  brush.circle(-60, -195, 70, false);
  brush.noFill();

  // 3 hatched rect
  brush.hatchStyle('2B', '#22221f', 1);
  brush.hatch(8, 0.4);
  brush.rect(80, -260, 160, 130);
  brush.noHatch();

  // 4 beginShape/vertex/endShape, filled
  brush.fill('#2fae6a', 60);
  brush.beginShape(0.4);
  brush.vertex(-320, 40); brush.vertex(-190, 0); brush.vertex(-130, 130); brush.vertex(-300, 160);
  brush.endShape(true);
  brush.noFill();

  // 5 every brush, one stroke each
  ['pen','rotring','2B','HB','2H','cpencil','pastel','crayon','charcoal','spray','marker']
    .forEach((b, i) => { brush.set(b, '#22221f', 4); brush.line(-60 + i*38, 40, -60 + i*38, 250); });
}
