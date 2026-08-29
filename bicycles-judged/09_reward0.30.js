function paint() {
    const WASH_COLOUR = '#ff6b6b'; // Bright red for wash
    const INK_COLOUR = '#1e1e1e'; // Near black for ink

    // Draw the wheels
    brush.fill(WASH_COLOUR, 80);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.circle(-200, 0, 80, false);
    brush.circle(200, 0, 80, false);
    brush.noFill();

    brush.set('rotring', INK_COLOUR, 2);
    brush.circle(-200, 0, 80, true);
    brush.circle(200, 0, 80, true);

    // Draw the frame
    brush.set('rotring', INK_COLOUR, 2);
    brush.beginShape(0.5);
    brush.vertex(-200, 0);
    brush.vertex(-100, 100);
    brush.vertex(100, 100);
    brush.vertex(200, 0);
    brush.endShape(true);

    // Draw the handlebars
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-100, 150, 0, 180);
    brush.line(0, 180, 100, 150);

    // Draw the pedals
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-120, -60, -90, -90);
    brush.line(-30, -60, -60, -90);
    brush.line(90, -60, 120, -90);
    brush.line(30, -60, 60, -90);
}
