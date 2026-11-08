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

package com.shatteredpixel.shatteredpixeldungeon.items.weapon.melee;

import com.shatteredpixel.shatteredpixeldungeon.Assets;
import com.shatteredpixel.shatteredpixeldungeon.Dungeon;
import com.shatteredpixel.shatteredpixeldungeon.actors.Actor;
import com.shatteredpixel.shatteredpixeldungeon.actors.Char;
import com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Buff;
import com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Invisibility;
import com.shatteredpixel.shatteredpixeldungeon.actors.buffs.Regeneration;
import com.shatteredpixel.shatteredpixeldungeon.actors.hero.Hero;
import com.shatteredpixel.shatteredpixeldungeon.actors.hero.luffy.Luffy;
import com.shatteredpixel.shatteredpixeldungeon.effects.RubberArm;
import com.shatteredpixel.shatteredpixeldungeon.items.rings.RingOfForce;
import com.shatteredpixel.shatteredpixeldungeon.mechanics.Ballistica;
import com.shatteredpixel.shatteredpixeldungeon.messages.Messages;
import com.shatteredpixel.shatteredpixeldungeon.scenes.CellSelector;
import com.shatteredpixel.shatteredpixeldungeon.scenes.GameScene;
import com.shatteredpixel.shatteredpixeldungeon.sprites.CharSprite;
import com.shatteredpixel.shatteredpixeldungeon.sprites.ItemSpriteSheet;
import com.shatteredpixel.shatteredpixeldungeon.ui.AttackIndicator;
import com.shatteredpixel.shatteredpixeldungeon.utils.GLog;
import com.watabou.noosa.audio.Sample;
import com.watabou.utils.Bundle;
import com.watabou.utils.Callback;
import com.watabou.utils.Random;

import java.util.ArrayList;

/**
 * Luffy's unique starting weapon.
 * - Base damage follows the fist tier, which rises by one for every boss slain (T1 -> T5).
 * - Upgrades always scale like a tier 4 weapon (+1 min / +5 max per level).
 * - A ring of force adds its level to the fist's level instead of its usual bonus.
 * - Charges power rubber techniques, starting with Gum-Gum Pistol.
 */
public class RubberFist extends MeleeWeapon {

	public static final String AC_PISTOL = "PISTOL";

	public static final int MAX_CHARGES = 10;
	public static final int PISTOL_RANGE = 3;

	{
		image = ItemSpriteSheet.RUBBER_FIST;
		hitSound = Assets.Sounds.HIT_CRUSH;
		hitSoundPitch = 1.1f;

		tier = 1;

		unique = true;
		bones = false;
	}

	public static int tierFor( int bossesSlain ){
		return Math.min(5, 1 + Math.max(0, bossesSlain));
	}

	//refreshes and returns the current tier, which depends on Luffy's progress
	private int curTier(){
		tier = tierFor(Luffy.bossesSlain());
		return tier;
	}

	@Override
	public int min(int lvl) {
		return  curTier() + //base
				lvl;        //level scaling
	}

	@Override
	public int max(int lvl) {
		return  5*(curTier()+1) +   //base
				lvl*5;              //level scaling, always like a tier 4 weapon
	}

	@Override
	public int STRReq(int lvl) {
		return STRReq(curTier(), lvl);
	}

	private static int forceBonus( Char owner ){
		return owner == null ? 0 : RingOfForce.armedDamageBonus(owner);
	}

	@Override
	public int damageRoll(Char owner) {
		int lvl = buffedLvl() + forceBonus(owner);
		int damage;
		if (owner instanceof Hero) {
			damage = Hero.heroDamageIntRange(min(lvl), max(lvl));
		} else {
			damage = Random.NormalIntRange(min(lvl), max(lvl));
		}
		damage = augment.damageFactor(damage);

		if (owner instanceof Hero) {
			int exStr = ((Hero)owner).STR() - STRReq();
			if (exStr > 0) {
				damage += Hero.heroDamageIntRange( 0, exStr );
			}
		}
		return damage;
	}

	// *** Charges ***

	public int chargeCap( Hero hero ){
		int cap = 3 + Math.max(0, level());
		if (hero != null) cap += Math.max(0, hero.STR() - STRReq());
		return Math.min(MAX_CHARGES, cap);
	}

	@Override
	public void activate(Char ch) {
		super.activate(ch);
		if (ch instanceof Hero && Luffy.isLuffy((Hero) ch)){
			Buff.affect(ch, Charger.class);
		}
	}

	@Override
	public String status() {
		Hero hero = Dungeon.hero;
		if (hero != null && isEquipped(hero) && hero.buff(Charger.class) != null) {
			return hero.buff(Charger.class).charges + "/" + chargeCap(hero);
		}
		return super.status();
	}

	// *** Actions ***

	@Override
	public String defaultAction() {
		if (Luffy.isLuffy(Dungeon.hero)){
			return AC_PISTOL;
		}
		return super.defaultAction();
	}

	@Override
	public ArrayList<String> actions(Hero hero) {
		ArrayList<String> actions = super.actions(hero);
		if (Luffy.isLuffy(hero)){
			actions.add(AC_PISTOL);
		}
		return actions;
	}

	@Override
	public String actionName(String action, Hero hero) {
		if (action.equals(AC_PISTOL)){
			return Messages.upperCase(Messages.get(this, "ac_pistol"));
		}
		return super.actionName(action, hero);
	}

	@Override
	public void execute(Hero hero, String action) {
		super.execute(hero, action);

		if (action.equals(AC_PISTOL)) {
			usesTargeting = false;
			if (!Luffy.isLuffy(hero)) {
				return;
			}
			if (!isEquipped(hero)) {
				GLog.w(Messages.get(this, "need_equip"));
				return;
			}
			Charger charger = Buff.affect(hero, Charger.class);
			if (charger.charges < 1) {
				GLog.w(Messages.get(this, "no_charge"));
				return;
			}
			usesTargeting = true;
			GameScene.selectCell(new CellSelector.Listener() {
				@Override
				public void onSelect(Integer cell) {
					if (cell != null) {
						pistol(hero, cell);
					}
				}

				@Override
				public String prompt() {
					return Messages.get(RubberFist.class, "pistol_prompt");
				}
			});
		}
	}

	public int pistolRange(){
		return PISTOL_RANGE;
	}

	//Gum-Gum Pistol: stretch an arm to punch an enemy up to a few tiles away
	private void pistol( Hero hero, int target ){
		Char enemy = Actor.findChar(target);
		if (enemy == null || enemy == hero || !Dungeon.level.heroFOV[target] || hero.isCharmedBy(enemy)) {
			GLog.w(Messages.get(this, "no_target"));
			return;
		}

		if (Dungeon.level.distance(hero.pos, target) > pistolRange()) {
			GLog.w(Messages.get(this, "out_of_range"));
			return;
		}

		Ballistica path = new Ballistica(hero.pos, target, Ballistica.PROJECTILE);
		if (path.collisionPos != target) {
			GLog.w(Messages.get(this, "blocked"));
			return;
		}

		hero.busy();
		//animation only, the hit itself happens once the arm reaches the target
		hero.sprite.attack(target, new Callback() {
			@Override
			public void call() {
				hero.sprite.idle();
			}
		});
		hero.sprite.showStatus(CharSprite.NEUTRAL, Messages.get(this, "pistol_shout"));
		Sample.INSTANCE.play(Assets.Sounds.MISS, 1f, 0.8f);

		hero.sprite.parent.add(new RubberArm(hero.sprite.center(), enemy.sprite.center(), new Callback() {
			@Override
			public void call() {
				Charger charger = Buff.affect(hero, Charger.class);
				charger.charges = Math.max(0, charger.charges - 1);

				AttackIndicator.target(enemy);
				if (hero.attack(enemy, 1f, 0, 1f)) {
					Sample.INSTANCE.play(Assets.Sounds.HIT_STRONG);
				}
				Invisibility.dispel();
				updateQuickslot();
				hero.spendAndNext(hero.attackDelay());
			}
		}));
	}

	// *** Info ***

	@Override
	public String info() {
		curTier();
		String info = super.info();
		if (Luffy.isLuffy(Dungeon.hero)) {
			info += "\n\n" + Messages.get(this, "luffy_desc", chargeCap(Dungeon.hero), pistolRange());
		}
		return info;
	}

	@Override
	public String statsInfo() {
		return Messages.get(this, "stats_desc");
	}

	@Override
	public int value() {
		//unique starting item, cannot be meaningfully sold
		return 0;
	}

	// *** Charge buff ***

	public static class Charger extends Buff {

		{
			revivePersists = true;
		}

		public int charges = 3;
		public float partialCharge = 0;

		private RubberFist fist(){
			if (target instanceof Hero){
				Hero hero = (Hero) target;
				if (hero.belongings.weapon() instanceof RubberFist){
					return (RubberFist) hero.belongings.weapon();
				}
				return hero.belongings.getItem(RubberFist.class);
			}
			return null;
		}

		public int chargeCap(){
			RubberFist fist = fist();
			if (fist == null) return 3;
			return fist.chargeCap((Hero) target);
		}

		@Override
		public boolean act() {
			int cap = chargeCap();
			if (charges < cap) {
				if (Regeneration.regenOn()) {
					//50 turns per charge when full, down to 30 turns when mostly empty
					float turns = Math.max(30f, 50f - 2f * (cap - charges));
					partialCharge += 1f / turns;
				}
				if (partialCharge >= 1) {
					charges++;
					partialCharge--;
					updateQuickslot();
				}
			} else {
				charges = Math.min(charges, cap);
				partialCharge = 0;
			}
			spend(TICK);
			return true;
		}

		private static final String CHARGES         = "charges";
		private static final String PARTIALCHARGE   = "partialCharge";

		@Override
		public void storeInBundle(Bundle bundle) {
			super.storeInBundle(bundle);
			bundle.put(CHARGES, charges);
			bundle.put(PARTIALCHARGE, partialCharge);
		}

		@Override
		public void restoreFromBundle(Bundle bundle) {
			super.restoreFromBundle(bundle);
			charges = bundle.getInt(CHARGES);
			partialCharge = bundle.getFloat(PARTIALCHARGE);
		}
	}
}
