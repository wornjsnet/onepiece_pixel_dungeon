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

package com.shatteredpixel.shatteredpixeldungeon.actors.hero.luffy;

import com.shatteredpixel.shatteredpixeldungeon.Challenges;
import com.shatteredpixel.shatteredpixeldungeon.Dungeon;
import com.shatteredpixel.shatteredpixeldungeon.actors.blobs.Electricity;
import com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Buff;
import com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Paralysis;
import com.shatteredpixel.shatteredpixeldungeon.actors.hero.Hero;
import com.shatteredpixel.shatteredpixeldungeon.actors.hero.HeroClass;
import com.shatteredpixel.shatteredpixeldungeon.actors.mobs.DM100;
import com.shatteredpixel.shatteredpixeldungeon.actors.mobs.Elemental;
import com.shatteredpixel.shatteredpixeldungeon.items.Item;
import com.shatteredpixel.shatteredpixeldungeon.items.armor.glyphs.Potential;
import com.shatteredpixel.shatteredpixeldungeon.items.food.Food;
import com.shatteredpixel.shatteredpixeldungeon.items.potions.PotionOfHealing;
import com.shatteredpixel.shatteredpixeldungeon.items.scrolls.ScrollOfRage;
import com.shatteredpixel.shatteredpixeldungeon.items.wands.WandOfLightning;
import com.shatteredpixel.shatteredpixeldungeon.items.weapon.enchantments.Shocking;
import com.shatteredpixel.shatteredpixeldungeon.items.weapon.melee.RubberFist;
import com.shatteredpixel.shatteredpixeldungeon.items.weapon.missiles.darts.ShockingDart;
import com.shatteredpixel.shatteredpixeldungeon.levels.traps.ShockingTrap;
import com.shatteredpixel.shatteredpixeldungeon.messages.Messages;
import com.shatteredpixel.shatteredpixeldungeon.sprites.CharSprite;
import com.shatteredpixel.shatteredpixeldungeon.utils.GLog;
import com.watabou.utils.Bundle;

/**
 * Monkey D. Luffy: class-specific logic that does not belong to a single item.
 * See docs/design/luffy.md for the full design.
 */
public class Luffy {

	public static boolean isLuffy( Hero hero ){
		return hero != null && hero.heroClass == HeroClass.LUFFY;
	}

	public static void initHero( Hero hero ){
		RubberFist fist = new RubberFist();
		fist.identify();
		hero.belongings.weapon = fist;
		fist.activate(hero);
		Dungeon.quickslot.setSlot(0, fist);

		//Luffy loves meat
		Item meat = new Food();
		if (!Challenges.isItemBlocked(meat)) meat.collect();

		new PotionOfHealing().identify();
		new ScrollOfRage().identify();

		Buff.affect(hero, RubberBody.class);
		Buff.affect(hero, Progress.class);
	}

	// *** Progress (bosses slain) ***

	public static int bossesSlain(){
		if (Dungeon.hero == null) return 0;
		Progress p = Dungeon.hero.buff(Progress.class);
		return p == null ? 0 : p.bossesSlain;
	}

	//called whenever a boss dies, bossNumber is 1-4 (Goo, Tengu, DM-300, Dwarf King)
	public static void onBossSlain( int bossNumber ){
		Hero hero = Dungeon.hero;
		if (!isLuffy(hero) || bossNumber <= 0) return;

		Progress p = Buff.affect(hero, Progress.class);
		if (bossNumber <= p.bossesSlain) return;
		p.bossesSlain = bossNumber;

		GLog.p(Messages.get(Luffy.class, "fist_tier_up", RubberFist.tierFor(bossNumber)));
		hero.sprite.showStatus(CharSprite.POSITIVE, Messages.get(Luffy.class, "fist_tier_up_short"));
		Item.updateQuickslot();
	}

	//tracks how far Luffy has progressed through the dungeon's bosses
	public static class Progress extends Buff {

		{
			revivePersists = true;
		}

		public int bossesSlain = 0;

		private static final String BOSSES_SLAIN = "bosses_slain";

		@Override
		public void storeInBundle(Bundle bundle) {
			super.storeInBundle(bundle);
			bundle.put(BOSSES_SLAIN, bossesSlain);
		}

		@Override
		public void restoreFromBundle(Bundle bundle) {
			super.restoreFromBundle(bundle);
			bossesSlain = bundle.getInt(BOSSES_SLAIN);
		}
	}

	// *** Innate traits: rubber insulation & paralysis immunity ***

	public static class RubberBody extends Buff {

		{
			revivePersists = true;

			//rubber insulation: immune to all electric damage
			immunities.add(WandOfLightning.class);
			immunities.add(Shocking.class);
			immunities.add(Electricity.class);
			immunities.add(ShockingDart.class);
			immunities.add(Elemental.ShockElemental.class);
			immunities.add(DM100.LightningBolt.class);
			immunities.add(ShockingTrap.class);
			immunities.add(Potential.class);

			//paralysis immunity
			immunities.add(Paralysis.class);
		}
	}
}
