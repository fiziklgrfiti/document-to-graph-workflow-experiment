# Black Templars Data Integrity Check

After reviewing the tables and content that I've transformed, I've verified the following to ensure data integrity:

## Unit Stat Profiles
1. **CHAPLAIN GRIMALDUS**
   - Original: M=6", T=4, SV=3+, W=4, LD=5+, OC=1
   - Transformed: M=6", T=4, SV=3+, W=4, LD=5+, OC=1
   - Status: ✓ Correct

2. **CENOBYTE SERVITOR**
   - Original: M=6", T=4, SV=3+, W=1, LD=8+, OC=(empty)
   - Transformed: M=6", T=4, SV=3+, W=1, LD=8+, OC=(empty)
   - Status: ✓ Correct

3. **CRUSADER SQUAD NEOPHYTES**
   - Original: M=6", T=4, SV=4+, W=2, LD=6+, OC=2
   - Transformed: M=6", T=4, SV=4+, W=2, LD=6+, OC=2
   - Status: ✓ Correct

4. **CRUSADER SQUAD OTHER MODELS**
   - Original: M=6", T=4, SV=3+, W=2, LD=6+, OC=2
   - Transformed: M=6", T=4, SV=3+, W=2, LD=6+, OC=2
   - Status: ✓ Correct

5. **HIGH MARSHAL HELBRECHT**
   - Original: M=6", T=4, SV=2+, W=5, LD=5+, OC=2
   - Transformed: M=6", T=4, SV=2+, W=5, LD=5+, OC=2
   - Status: ✓ Correct

## Weapon Profiles
1. **Plasma pistol – standard**
   - Original: Range=12", A=1, BS=2+, S=7, AP=-2, D=1
   - Transformed: Range=12", A=1, BS=2+, S=7, AP=-2, D=1
   - Status: ✓ Correct

2. **Artificer crozius**
   - Original: Range=Melee, A=5, WS=2+, S=6, AP=-2, D=2
   - Transformed: Range=Melee, A=5, WS=2+, S=6, AP=-2, D=2
   - Status: ✓ Correct

3. **Thunder hammer**
   - Original: Range=Melee, A=2, WS=4+, S=8, AP=-2, D=2
   - Transformed: Range=Melee, A=2, WS=4+, S=8, AP=-2, D=2
   - Status: ✓ Correct

4. **Twin lightning claws**
   - Original: Range=Melee, A=3, WS=3+, S=5, AP=-2, D=1
   - Transformed: Range=Melee, A=3, WS=3+, S=5, AP=-2, D=1
   - Status: ✓ Correct

5. **Lancer laser destroyer**
   - Original: Range=72", A=2, BS=3+, S=14, AP=-4, D=D6+3
   - Transformed: Range=72", A=2, BS=3+, S=14, AP=-4, D=D6+3
   - Status: ✓ Correct

## Special Abilities
1. **Litanies of the Devout**
   - Original: "While Chaplain Grimaldus is leading a unit, each time a model in that unit makes a melee attack, you can re-roll the Hit roll."
   - Transformed: Same text preserved
   - Status: ✓ Correct

2. **Righteous Zeal**
   - Original: "You can re-roll Advance and Charge rolls made for this unit."
   - Transformed: Same text preserved
   - Status: ✓ Correct

3. **Vow-sworn Bladesmen**
   - Original: "At the start of the Fight phase, you can select one of the following effects to apply to melee weapons equipped by models in this unit until the end of the phase: Add 1 to the Attacks characteristic of those weapons. Add 1 to the Damage characteristic of those weapons."
   - Transformed: Same content preserved with proper formatting
   - Status: ✓ Correct

## Table Structure
- All tables maintain consistent column counts across rows
- Header rows are properly aligned with the data rows
- Markdown table formatting is correctly implemented with proper cell separators

## Templar Vows
- All four vows (Suffer Not the Unclean to Live, Uphold the Honour of the Emperor, Abhor the Witch Destroy the Witch, Accept Any Challenge No Matter the Odds) have been correctly preserved with their exact effects

## Stratagems
- All six stratagems (Fervent Acclamation, Devout Push, No Escape, Vicious Riposte, Armour of Contempt, Crusader's Wrath) are preserved with correct CP costs, timing, targets, and effects

## Enhancements
- All four enhancements (Perdition's Edge, Witchseeker Bolts, Sigismund's Seal, Tännhauser's Bones) are preserved with correct requirements and effects

## Wargear Options
- All unit wargear options are preserved with correct formatting and hierarchical structures

## Notes on the Conversion Process
- Special characters (like umlauts in "Tännhauser") are correctly preserved
- Weapon special rules in brackets (like [HAZARDOUS]) are correctly preserved
- Footnote references (like * and **) are preserved with their explanations
- Unit composition sections maintain correct formatting and information

Overall, the transformation from text blocks to proper tables has been completed with no data integrity errors. The tabular format significantly improves readability while maintaining all the original game statistics and rules information.