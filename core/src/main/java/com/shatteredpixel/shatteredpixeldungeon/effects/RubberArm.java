/*
 * One Piece Pixel Dungeon
 * Based on Shattered Pixel Dungeon
 * Copyright (C) 2014-2026 Evan Debenham
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>
 */

package com.shatteredpixel.shatteredpixeldungeon.effects;

import com.shatteredpixel.shatteredpixeldungeon.Assets;
import com.watabou.noosa.Game;
import com.watabou.noosa.Group;
import com.watabou.noosa.Image;
import com.watabou.utils.Callback;
import com.watabou.utils.PointF;

import java.util.ArrayList;

/**
 * Luffy's arm stretching out to a target and snapping back (Gum-Gum techniques).
 * The callback fires when the fist reaches the target.
 * Art: effects/rubber_arm.png, a 4x6 arm segment followed by an 8x8 fist.
 */
public class RubberArm extends Group {

	private static final float A = 180 / (float)Math.PI;

	private static final float EXTEND_TIME_BASE = 0.12f;
	private static final float RETRACT_TIME = 0.12f;
	private static final float SEGMENT_SPACING = 3f;

	private final PointF from;
	private final PointF to;
	private final float distance;
	private final float angle;
	private final float extendTime;

	private final ArrayList<Image> segments = new ArrayList<>();
	private final Image fist;

	private Callback callback;
	private float time = 0;

	public RubberArm(PointF from, PointF to, Callback callback) {
		super();
		this.from = from;
		this.to = to;
		this.callback = callback;

		float dx = to.x - from.x;
		float dy = to.y - from.y;
		distance = (float)Math.hypot(dx, dy);
		angle = (float)Math.atan2(dy, dx) * A;
		extendTime = EXTEND_TIME_BASE + distance / 600f;

		int count = Math.max(1, (int)(distance / SEGMENT_SPACING));
		for (int i = 0; i < count; i++) {
			Image seg = new Image(Assets.Effects.RUBBER_ARM, 0, 0, 4, 8);
			seg.origin.set(2, 4);
			seg.angle = angle;
			segments.add(seg);
			add(seg);
		}

		fist = new Image(Assets.Effects.RUBBER_ARM, 4, 0, 8, 8);
		fist.origin.set(4, 4);
		fist.angle = angle;
		add(fist);

		place(0);
	}

	//progress: 0 = arm fully retracted, 1 = fist at the target
	private void place(float progress) {
		float len = distance * progress;
		float cos = (float)Math.cos(angle / A);
		float sin = (float)Math.sin(angle / A);

		for (int i = 0; i < segments.size(); i++) {
			Image seg = segments.get(i);
			float d = i * SEGMENT_SPACING;
			seg.visible = d < len;
			seg.x = from.x + cos * d - seg.origin.x;
			seg.y = from.y + sin * d - seg.origin.y;
		}

		fist.x = from.x + cos * len - fist.origin.x;
		fist.y = from.y + sin * len - fist.origin.y;
	}

	@Override
	public void update() {
		super.update();
		time += Game.elapsed;

		if (time < extendTime) {
			place(time / extendTime);
		} else {
			if (callback != null) {
				Callback c = callback;
				callback = null;
				place(1);
				c.call();
			}
			float back = (time - extendTime) / RETRACT_TIME;
			if (back >= 1) {
				killAndErase();
			} else {
				place(1 - back);
			}
		}
	}
}
