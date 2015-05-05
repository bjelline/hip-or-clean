--
-- Name: businesses; Type: TABLE; Schema: public; Owner: bjelline; Tablespace: 
--

DROP TABLE IF EXISTS violations;
DROP MATERIALIZED VIEW IF EXISTS newest_inspection;
DROP TABLE IF EXISTS inspections;
DROP TABLE IF EXISTS inspection_businesses;
DROP TABLE IF EXISTS foursquare_cache;

CREATE TABLE foursquare_cache (
  "id"  varchar(30) primary key,
  "name"  varchar(100),
  "phone" varchar(15),
  "verified"  boolean default false,

  "price_tier"  smallint,
  "rating" decimal(4,2),

  "address"  varchar(100),
  "lat"  decimal(10,7),
  "lng"  decimal(10,7),
  "city"  varchar(50),
  "cc" varchar(2) DEFAULT '',
  "country"  varchar(50),
  "state"  varchar(2) default '',

  "canonicalUrl" varchar(100),
  "bestPhoto"  varchar(150) default '',
  "url"  varchar(100) default '',

  "likes_count"  smallint,
  "checkinsCount" smallint,
  "usersCount" smallint,
  "hereNow_count"  smallint,
  "visitsCount"  smallint,
  "tipCount"  smallint
);

--
-- Name: businesses; Type: TABLE; Schema: public; Owner: bjelline; Tablespace: 
--

CREATE TABLE inspection_businesses (
    "camis" bigint PRIMARY KEY,
    "id"  varchar(30) NULL REFERENCES foursquare_cache(id) ON DELETE SET NULL,
    "dba" varchar(120),
    "boro" varchar(20),
    "building" varchar(20),
    "street" varchar(120),
    "zipcode" varchar(10),
    "phone" varchar(15),
    "cuisine_description" varchar(100)
);

--
-- Name: businesses; Type: TABLE; Schema: public; Owner: bjelline; Tablespace: 
--

CREATE TABLE inspections (
    "camis" bigint REFERENCES inspection_businesses(camis) ON DELETE CASCADE,
    "inspection_date" date,
    "action" varchar(200),
    "violation_code" varchar(3),
    "violation_description" text,
    "critical_flag" varchar(20),
    "score" int NULL,
    "grade" varchar(1) NULL,
    "grade_date" date,
    "record_date" date,
    "inspection_type" varchar(120),
    PRIMARY KEY ("camis", "inspection_date")
);

CREATE MATERIALIZED VIEW newest_inspection AS 
  SELECT camis, max(inspection_date) inspection_date
  FROM inspection_businesses 
  LEFT JOIN inspections USING(camis) 
  GROUP BY camis;


CREATE TABLE violations(
  id serial primary key,
  "violation_description" text
);
INSERT INTO violations (violation_description) VALUES
('Alcohol and pregnancy warning sign not posted'),
('Choking first aid poster not posted'),
('No Smoking and/or Smoking Permitted sign not conspicuously posted'),
('Wash hands sign not posted at hand wash facility'),
('5 grams or more of artificial trans fat per serving, is being stored, distributed, held for service, used in preparation of a menu item or served'),
('5 grams or more of trans fat per serving, is being stored, distributed, held for service, used in preparation of a menu item, or served'),
('A food containing 0'),
('A food containing artificial trans fat, with 0'),
('Accurate thermometer not provided in refrigerated or hot holding equipment'),
('Alcohol and Pregnancy warning sign, inspection report sign; not posted'),
('Appropriately scaled metal stem-type thermometer or thermocouple not provided or used to evaluate temperatures of potentially hazardous foods during cooking, cooling, reheating and holding'),
('Ashtray present in smoke-free area'),
('Bulb not shielded or shatterproof'),
('Bulb not shielded or shatterproof, in areas where there is extreme heat, temperature changes, or where accidental contact may occur'),
('CO ~1 3 ppm'),
('CPR sign not posted, equipment (resuscitation masks, adult & pediatric, latex gloves) not provided'),
('Caloric content not posted on menus, menu boards or food tags, in a food service establishment that is 1 of 15 or more outlets operating the same type of business nationally under common ownership or control, or as a franchise or doing business under the same name, for each menu item that is served in portions, the size and content of which are standardized'),
('Caloric content range (minimum to maximum) not posted on menus and or menu boards for each flavor, variety and size of each menu item that is offered for sale in different flavors, varieties and sizes'),
('Canned food product observed dented and not segregated from other consumable food items'),
('Canned food product observed swollen, leaking or rusted, and not segregated from other consumable food items '),
('Choking first aid poster not posted'),
('Cold food held above 41°F (smoked fish above 38°F) except during necessary preparation'),
('Cold food item held above 41º F (smoked fish and reduced oxygen packaged foods above 38 ºF) except during necessary preparation'),
('Covered garbage receptacle not provided or inadequate, except that garbage receptacle may be uncovered during active use'),
('Cross connection in potable water supply system observed'),
('Current letter grade card not posted'),
('Current valid permit, registration or other authorization to operate establishment not available'),
('Document issued by the Board of Health, Commissioner or Department unlawfully reproduced or altered'),
('Duties of an officer of the Department interfered with or obstructed'),
('Effective hair restraint not worn in an area where food is prepared'),
('Eggs found dirty/cracked; liquid, frozen or powdered eggs not pasteurized'),
('Evidence of mice or live mice present in facilitys food and/or non-food areas'),
('Evidence of rats or live rats present in facilitys food and/or non-food areas'),
('Facility not free from unsafe, hazardous, offensive or annoying conditions'),
('Facility not vermin proof'),
('Failure to comply with an Order of the Board of Health, Commissioner, or Department'),
('Filth flies include house flies, little house flies, blow flies, bottle flies and flesh flies'),
('Filth flies or food/refuse/sewage-associated (FRSA) flies present in facilitys food and/or non-food areas'),
('Flavored tobacco products sold or offered for sale'),
('Food Protection Certificate not held by supervisor of food operations'),
('Food allergy information poster not conspicuously posted where food is being prepared or processed by food workers'),
('Food allergy information poster not posted in language understood by all food workers'),
('Food contact surface improperly constructed or located'),
('Food contact surface not properly maintained'),
(' Food contact surface not properly washed, rinsed and sanitized after each use and following any activity when contamination may have occurred'),
('Food from unapproved or unknown source or home canned'),
('Food item spoiled, adulterated, contaminated or cross-contaminated'),
('Food not cooked to required minimum temperature'),
('Food not cooled by an approved method whereby the internal product temperature is reduced from 140º F to 70º F or less within 2 hours, and from 70º F to 41º F or less within 4 additional hours'),
('Food not labeled in accordance with HACCP plan'),
('Food not protected from potential source of contamination during storage, preparation, transportation, display or service'),
('Food prepared from ingredients at ambient temperature not cooled to 41º F or below within 4 hours'),
('Food service operation occurring in room used as living or sleeping quarters'),
('Food worker does not use proper utensil to eliminate bare hand contact with food that will not receive adequate additional heat treatment'),
('Food worker does not wash hands thoroughly after using the toilet, coughing, sneezing, smoking, eating, preparing raw foods or otherwise contaminating hands'),
('Food worker prepares food or handles utensil when ill with a disease transmissible by food, or have exposed infected cut or burn on hand'),
('Food, food preparation area, food storage area, area used by employees or patrons, contaminated by sewage or liquid waste'),
('Food/refuse/sewage-associated flies include fruit flies, drain flies and Phorid flies'),
('Garbage receptacles not provided or inadequate'),
('Garbage storage area not properly constructed or maintained; grinder or compactor dirty'),
('HACCP plan not approved or approved HACCP plan not maintained on premises'),
('Hand washing facility not provided in or near food preparation area and toilet room'),
(' Harborage or conditions conducive to attracting vermin to the premises and/or allowing vermin to exist'),
('Harborage or conditions conducive to vermin exist'),
('Harmful, noxious gas or vapor detected'),
('Health warning not present on Smoking Permitted'),
('Hot and cold running water at adequate pressure to enable cleanliness of employees not provided at facility'),
('Hot food item not held at or above 140º F'),
('Hot food item that has been cooked and refrigerated is being held for service without first being reheated to 1 65º F or above within 2 hours'),
('Immersion basket not provided, used or of incorrect size'),
('Improper drying practices'),
('Incorrect manual technique'),
('Inspection report sign not posted'),
('Insufficient or no refrigerated or hot holding equipment to keep potentially hazardous foods at required temperatures'),
('Letter Grade or Grade Pending card not conspicuously posted and visible to passersby'),
('Lighting inadequate'),
('Lighting inadequate; permanent lighting not provided in food preparation areas, ware washing areas, and storage rooms'),
('Live animals other than fish in tank or service animal present in facilitys food and/or non-food areas'),
('Live roaches present in facilitys food and/or non-food areas'),
('Manufacture of frozen dessert not authorized on Food Service Establishment permit'),
('Meat, fish or molluscan shellfish served raw or undercooked without prior notification to customer'),
('Mechanical or natural ventilation system not provided, improperly installed, in disrepair and/or fails to prevent excessive build-up of grease, heat, steam condensation vapors, odors, smoke, and fumes'),
('Milk or milk product undated, improperly dated or expired'),
('No facilities available to wash, rinse and sanitize utensils and/or equipment'),
('Non-food contact surface improperly constructed'),
('Non-food contact surface or equipment improperly maintained'),
('Non-food contact surface or equipment improperly maintained and/or not properly sealed, raised, spaced or movable to allow accessibility for cleaning on all sides, above and underneath the unit'),
('Notice of the Department of Board of Health mutilated, obstructed, or removed'),
('Nuisance created or allowed to exist'),
('Open bait station used'),
('Operator failed to make good faith effort to inform smokers of the Smoke-free Act prohibition of smoking'),
('Original label for tobacco products sold or offered for sale'),
('Other general violation'),
('Out-of package sale of tobacco products observed'),
('Outer garment soiled with possible contaminant'),
('Permit not conspicuously displayed'),
('Personal cleanliness inadequate'),
('Pesticide use not in accordance with label or applicable laws'),
('Plumbing not properly installed or maintained; anti-siphonage or backflow prevention device not provided where required; equipment or floor not properly drained; sewage disposal system in disrepair or not functioning properly'),
('Potable water supply inadequate'),
('Precooked potentially hazardous food from commercial food processing establishment that is supposed to be heated, but is not heated to 140º F within 2 hours'),
('Precooked potentially hazardous food from commercial food processing establishment that is supposed to be heated, but is not heated to 140Âº F within 2 hours'),
('Prohibited chemical used/stored'),
('Proper sanitization not provided for utensil ware washing operation'),
('ROP processing equipment not approved by DOHMH'),
('Raw food not properly washed prior to serving'),
('Raw, cooked or prepared food is adulterated, contaminated, cross-contaminated, or not discarded in accordance with HACCP plan'),
('Records and logs not maintained to demonstrate that HACCP plan has been properly implemented'),
('Reduced oxygen packaged (ROP) fish not frozen before processing; or ROP foods prepared on premises transported to another site'),
('Reduced oxygen packaged (ROP) foods not cooled by an approved method whereby the internal food temperature is reduced to 38º F within two hours of cooking and if necessary further cooled to a temperature of 34º F within six hours of reaching 38º F'),
('Refrigeration used to implement HACCP plan not equipped with an electronic system that continuously monitors time and temperature'),
('Resuscitation equipment: exhaled air resuscitation masks (adult & pediatric), latex gloves, sign not posted'),
('Sanitized equipment or utensil, including in-use food dispensing utensil, improperly used or stored'),
('Sewage disposal system improper or unapproved'),
('Shellfish not from approved source, improperly tagged/labeled; tags not retained for 90 days'),
('Sign prohibiting sale of tobacco products to minors not conspicuously posted'),
('Single service item reused, improperly stored, dispensed; not used when required'),
('Smoke free workplace smoking policy inadequate, not posted, not provided to employees'),
('Soap and an acceptable hand-drying device not provided'),
('Specific caloric content or range thereof not posted on menus, menu boards or food tags for each menu item offered as a combination meal with multiple options that are listed as single items'),
('Test kit and thermometer not provided or used'),
('Thawing procedures improper'),
('The original nutritional fact labels and/or ingredient label for a cooking oil, shortening or margarine or food item sold in bulk, or acceptable manufacturers documentation not maintained on site'),
('The original nutritional fact labels and/or ingredient label for cooking oil, shortening or margarine or food item sold in bulk, or acceptable manufacturer\s documentation not maintained on site'),
('Tobacco use, eating, or drinking from open container in food preparation, food storage or dishwashing area observed'),
('Toilet facility not maintained and provided with toilet paper, waste receptacle and self-closing door'),
('Toilet facility not provided for employees or for patrons when required'),
('Toilet facility used by women does not have at least one covered garbage receptacle'),
('Toxic chemical improperly labeled, stored or used such that food contamination may occur'),
('Unacceptable material used'),
('Unpasteurized milk or milk product present'),
('Unprotected food re-served'),
('Unprotected potentially hazardous food re-served'),
('Water or ice not potable or from unapproved source'),
('Whole frozen poultry or poultry breasts, other than a single portion, is being cooked frozen or partially thawed'),
('Wiping cloths soiled or not stored in sanitizing solution'),
('Work place smoking policy inadequate, not posted, not provided');
