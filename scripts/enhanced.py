import requests
import csv
import uuid

request = requests.get("https://sw5eapi.azurewebsites.net/api/enhancedItem")

data = request.json()

rarity_map = {
    1: "Standard",
    2: "Premium",
    3: "Prototype",
    4: "Advanced",
    5: "Legendary",
    6: "Artifact",
}

type_map = {"1":{"body":{"value":"Body","parent":1,"id":1},"feet":{"value":"Feet","parent":1,"id":2},"finger":{"value":"Finger","parent":1,"id":3},"hands":{"value":"Hands","parent":1,"id":4},"other":{"value":"Other","parent":1,"id":5},"head":{"value":"Head","parent":1,"id":6},"shoulders":{"value":"Shoulders","parent":1,"id":7},"waist":{"value":"Waist","parent":1,"id":8},"wrists":{"value":"Wrists","parent":1,"id":9},"legs":{"value":"Legs","parent":1,"id":10},"neck":{"value":"Neck","parent":1,"id":11}},"2":{"any":{"value":"Any","parent":2,"id":24},"anyheavy":{"value":"Any Heavy","parent":2,"id":25},"anymedium":{"value":"Any Medium","parent":2,"id":26},"anylight":{"value":"Any Light","parent":2,"id":27},"specific":{"value":"Specific","parent":2,"id":28}},"3":{"adrenals":{"value":"Adrenals","parent":3,"id":15},"explosives":{"value":"Explosives","parent":3,"id":16},"poisons":{"value":"Poisons","parent":3,"id":17},"stimpacs":{"value":"Stimpacs","parent":3,"id":18},"other":{"value":"Other","parent":3,"id":19},"barriers":{"value":"Barriers","parent":3,"id":20}},"4":{"enhancement":{"value":"Enhancement","parent":4,"id":12},"replacement":{"value":"Replacement","parent":4,"id":13},"other":{"value":"Other","parent":4,"id":14}},"5":{"part":{"value":"Part","parent":5,"id":21},"protocol":{"value":"Protocol","parent":5,"id":22},"other":{"value":"Other","parent":5,"id":23}},"6":{"force":{"value":"Force","parent":6,"id":43},"tech":{"value":"Tech","parent":6,"id":44},"other":{"value":"Other","parent":6,"id":45}},"7":{"armoring":{"value":"Armoring","parent":7,"id":47},"augment":{"value":"Augment","parent":7,"id":48},"barrel":{"value":"Barrel","parent":7,"id":49},"conductor":{"value":"Conductor","parent":7,"id":50},"crystal":{"value":"Crystal","parent":7,"id":51},"cycler":{"value":"Cycler","parent":7,"id":52},"dataport":{"value":"Dataport","parent":7,"id":53},"edge":{"value":"Edge","parent":7,"id":54},"emitter":{"value":"Emitter","parent":7,"id":55},"energychannel":{"value":"Energy Channel","parent":7,"id":56},"energycore":{"value":"Energy Core","parent":7,"id":57},"grip":{"value":"Grip","parent":7,"id":58},"lens":{"value":"Lens","parent":7,"id":59},"matrix":{"value":"Matrix","parent":7,"id":60},"motherboard":{"value":"Motherboard","parent":7,"id":61},"overlay":{"value":"Overlay","parent":7,"id":62},"powercell":{"value":"Power Cell","parent":7,"id":63},"processor":{"value":"Processor","parent":7,"id":64},"projector":{"value":"Projector","parent":7,"id":65},"reinforcement":{"value":"Reinforcement","parent":7,"id":66},"shielding":{"value":"Shielding","parent":7,"id":67},"stabilizer":{"value":"Stabilizer","parent":7,"id":68},"storage":{"value":"Storage","parent":7,"id":69},"targeting":{"value":"Targeting","parent":7,"id":70},"underlay":{"value":"Underlay","parent":7,"id":71},"vibratorcell":{"value":"Vibrator Cell","parent":7,"id":72},"other":{"value":"Other","parent":7,"id":73},"weave":{"value":"Weave","parent":7,"id":74},"inlay":{"value":"Inlay","parent":7,"id":75}},"8":{"light":{"value":"Light","parent":8,"id":29},"medium":{"value":"Medium","parent":8,"id":30},"heavy":{"value":"Heavy","parent":8,"id":31},"specific":{"value":"Specific","parent":8,"id":32},"any":{"value":"Any","parent":8,"id":33}},"9":{"any":{"value":"Any","parent":9,"id":34},"anyblaster":{"value":"Any Blaster","parent":9,"id":35},"anyvibroweapon":{"value":"Any Vibroweapon","parent":9,"id":36},"anylightweapon":{"value":"Any Lightweapon","parent":9,"id":37},"anyblasterwithproperty":{"value":"Any Blaster With Property","parent":9,"id":38},"anyvirboweaponwithproperty":{"value":"Any Virboweapon With Property","parent":9,"id":39},"anylightweaponwithproperty":{"value":"Any Lightweapon With Property","parent":9,"id":40},"anywithproperty":{"value":"Any With Property","parent":9,"id":41},"specific":{"value":"Specific","parent":9,"id":42}},"10":{"art":{"value":"Art","parent":10,"id":76},"jewel":{"value":"Jewel","parent":10,"id":77},"sculpture":{"value":"Sculpture","parent":10,"id":78},"relic":{"value":"Relic","parent":10,"id":79},"other":{"value":"Other","parent":10,"id":80}}}

perm_costs = {
    1: 2500,
    2: 15000,
    3: 45000,
    4: 90000,
    5: 150000
}

mod_costs = {
    1: 1000,
    2: 5000,
    3: 15000,
    4: 45000,
    5: 75000,
    6: 100000
}

output = [
    [
        "id",
        "name",
        "type",      
        "rarity",
        "attunement",
        "text",
        "prerequisite",
        "subtype_ft",
        "subtype",
        "cost",
        "source"
    ]
]

for obj in data:
   def get_value(key: str):
        val = obj.get(key)

        if val == "None":
            return None
        return val
   
   def get_subtype_key():
       out = None
       subtypes = ['cyberneticAugmentationType', 'droidCustomizationType', 'adventuringGearType','enhancedArmorType', 'consumableType', 'focusType', 'enhancedShieldType', 'enhancedWeaponType', 'itemModificationType', 'valuableType']

       for s in subtypes:
           if out := get_value(s):
               return out.lower()
   subtype = None
   cost = 0
   subtype_map = type_map.get(str(obj.get('typeEnum')))

   if not subtype_map:
       print(f"Issues with {get_value('name')}")

   if key := get_subtype_key():
       subtype = subtype_map.get(get_subtype_key())
        
       if not subtype:
           print(get_subtype_key())

   rarity = get_value('rarityOptionsEnum')[0] 

   if obj.get('typeEnum') in [3, 7] or (subtype and subtype in []) or (obj.get('typeEnum') == 1 and not subtype):
       cost = mod_costs.get(rarity,0)
   else:
       cost = perm_costs.get(rarity, 0)

   line = [
       uuid.uuid4(),
       get_value('name'),
       get_value('typeEnum'),
       rarity,
       get_value('requiresAttunement'),
       get_value('text'),
       get_value('prerequisite'),
       None if subtype and subtype["value"].lower() not in ["special", "specific", "other"] else get_value('subtype').title() if get_value('subtype') else None,
       subtype.get('id') if subtype else None,
       cost,
       get_value('contentSourceEnum'),
   ]

   output.append(line)

print(len(output))

with open("data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(output)
    