CREATE TABLE bmw_car_models (
    model_id VARCHAR(20) PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    series VARCHAR(50) NOT NULL,
    body_type VARCHAR(50) NOT NULL,
    official_price DECIMAL(10,2) NOT NULL,
    engine_power INT, -- Unit: kW, NULL indicates pure electric
    max_torque INT, -- Unit: N·m
    acceleration_time DECIMAL(4,2), -- 0-100km/h acceleration time, Unit: seconds
    electric_range INT, -- Pure electric range, Unit: km, NULL indicates non-pure electric
    main_config TEXT,
    suitable_people VARCHAR(255),
    usage_scenario VARCHAR(255),
    exterior_style VARCHAR(100),
    interior_material VARCHAR(100),
    fuel_type VARCHAR(20) NOT NULL -- Fuel Type: Petrol, Diesel, Pure Electric, Plug-in Hybrid
);

INSERT INTO bmw_car_models VALUES
-- 1 Series
('BMW001', '125i M Sport Shadow Edition', '1 Series', 'Sedan', 24.68, 141, 280, 7.5, NULL, '10.25-inch central control screen, panoramic sunroof, LED headlights, automatic parking', 'Young urban professionals, first-time car buyers', 'Urban commuting, daily transportation', 'Stylish and dynamic', 'Sensatec Synthetic Leather', 'Petrol'),

-- 2 Series
('BMW002', '225i Convertible Coupe M Sport Package', '2 Series', 'Convertible Coupe', 30.98, 135, 270, 7.6, NULL, 'Soft-top convertible, sports seats, Harman Kardon sound system', 'Young fashion enthusiasts, driving enthusiasts', 'Weekend outings, leisure driving', 'Personalized and sporty', 'Leather/Alcantara Combination', 'Petrol'),
('BMW003', '225i xDrive Gran Coupe M Sport Package', '2 Series', 'Coupe', 28.98, 135, 270, 7.4, NULL, 'Frameless doors, all-wheel drive, digital instrument cluster', 'Young professionals', 'Urban driving, short-distance trips', 'Sporty and elegant', 'Sensatec Synthetic Leather', 'Petrol'),

-- 3 Series
('BMW004', '325Li M Sport Package', '3 Series', 'Sedan', 35.39, 135, 300, 8.1, NULL, '12.3-inch full LCD instrument panel, 14.9-inch central control screen, power tailgate', 'Young families, business professionals', 'Daily commuting, business trips', 'Sporty and grand', 'Sensatec Synthetic Leather', 'Petrol'),
('BMW005', '330Li xDrive M Sport Shadow Edition', '3 Series', 'Sedan', 44.99, 180, 400, 6.2, NULL, 'Harman Kardon sound system, 360-degree panoramic camera, Level 2 driving assistance', 'Mid-to-high-end workplace professionals', 'Long-distance driving, business activities', 'Luxurious and sporty', 'Leather Seats', 'Petrol'),

-- 4 Series
('BMW006', '425i Convertible Coupe M Sport Package', '4 Series', 'Convertible Coupe', 53.98, 135, 300, 8.2, NULL, 'Electric soft-top convertible, sports suspension, variable steering ratio', 'Fashion elites, driving enthusiasts', 'Leisure driving, vacation trips', 'Dynamic and eye-catching', 'Leather Seats', 'Petrol'),
('BMW007', '430i xDrive Coupe M Sport Shadow Edition', '4 Series', '2-Door Coupe', 58.58, 180, 400, 5.8, NULL, 'All-wheel drive, M Sport brakes, paddle shifters', 'Performance enthusiasts, high-end consumers', 'Mountain road driving, sports experience', 'Aggressively sporty', 'Nappa Leather', 'Petrol'),

-- 5 Series
('BMW008', '530Li Luxury Line M Sport Package', '5 Series', 'Sedan', 47.55, 185, 350, 6.9, NULL, 'Comfort seats, 4-zone automatic air conditioning, power tailgate', 'Business professionals, mid-to-high-end families', 'Business reception, long-distance travel', 'Stable and grand', 'Leather Seats', 'Petrol'),
('BMW009', '530Le Pioneer Edition M Sport Package', '5 Series', 'Sedan', 51.23, 135, 300, 6.7, 95, 'Plug-in hybrid system, air suspension, advanced driving assistance', 'Eco-conscious users, business professionals', 'Daily commuting, business trips', 'Luxurious and stable', 'Premium Leather', 'Plug-in Hybrid'),

-- 6 Series GT
('BMW010', '630i Luxury Design Package', '6 Series GT', 'Hatchback Sedan', 58.39, 190, 400, 6.9, NULL, 'Frameless doors, air suspension, electric rear spoiler', 'Business professionals pursuing individuality', 'Long-distance travel, business trips', 'Elegant and dynamic', 'Nappa Leather', 'Petrol'),

-- 7 Series
('BMW011', '730Li Luxury Package', '7 Series', 'Sedan', 82.80, 195, 400, 6.7, NULL, 'Premium Nappa leather, starry panoramic sunroof, Magic Carpet air suspension', 'Corporate executives, successful individuals', 'Business reception, high-end travel', 'Luxurious and grand', 'Nappa Leather', 'Petrol'),
('BMW012', 'i7 xDrive60 Luxury Package', '7 Series', 'Sedan', 145.90, NULL, 745, 4.7, 650, 'Pure electric drive, rear-row floating giant screen, Bowers & Wilkins Diamond Surround Sound System', 'High-end users with strong eco-awareness', 'Business reception, luxury travel', 'Future luxury', 'Merino Full Leather', 'Pure Electric'),

-- 8 Series
('BMW013', '840i 2-Door Coupe', '8 Series', '2-Door Coupe', 96.80, 250, 500, 4.9, NULL, 'Adaptive M suspension, integral active steering, laser headlights', 'High-end consumers, sports car enthusiasts', 'Sports driving, special occasions', 'Luxurious and sporty', 'Merino Full Leather', 'Petrol'),
('BMW014', '840i Convertible Coupe', '8 Series', 'Convertible Coupe', 109.80, 250, 500, 5.2, NULL, 'Intelligent drag-reducing convertible top, neck warming system, premium fragrance system', 'High-end elites, individuals with taste for life', 'Leisure driving, social events', 'Elegant and luxurious', 'Merino Full Leather', 'Petrol'),

-- X1
('BMW015', 'X1 sDrive25Li Advantage Edition', 'X1', 'SUV', 28.89, 150, 300, 8.1, NULL, 'Panoramic sunroof, power tailgate, comfort access', 'Young families, urban users', 'Urban commuting, family outings', 'Stylish and practical', 'Sensatec Synthetic Leather', 'Petrol'),
('BMW016', 'iX1 xDrive30 Premium Edition', 'X1', 'SUV', 33.99, NULL, 365, 5.7, 410, 'Pure electric drive, all-wheel drive, fast charging function', 'Young eco-friendly families', 'Urban commuting, short-distance trips', 'Modern technology', 'Sensatec Synthetic Leather', 'Pure Electric'),

-- X3
('BMW017', 'X3 xDrive30i Advantage Edition M Sport Package', 'X3', 'SUV', 43.68, 185, 350, 6.8, NULL, 'Intelligent all-wheel drive, M Sport package, comfort seats', 'Middle-class families, outdoor enthusiasts', 'Urban driving, light off-roading', 'Tough and sporty', 'Sensatec Synthetic Leather', 'Petrol'),
('BMW018', 'iX3 Premium Edition', 'X3', 'SUV', 40.50, NULL, 400, 6.8, 500, 'Pure electric drive, fast charging technology, aerodynamic wheels', 'Eco-conscious users, urban families', 'Urban commuting, daily travel', 'Modern and minimalist', 'Sensatec Synthetic Leather', 'Pure Electric'),

-- X5
('BMW019', 'X5 xDrive40Li Luxury Edition M Sport Package', 'X5', 'SUV', 82.90, 245, 450, 6.0, NULL, 'Intelligent all-wheel drive, air suspension, starry panoramic sunroof', 'High-end families, business professionals', 'Long-distance travel, off-road adventures', 'Grand and luxurious', 'Nappa Leather', 'Petrol'),
('BMW020', 'X5 xDrive45e Executive Edition', 'X5', 'SUV', 85.90, 210, 450, 5.6, 90, 'Plug-in hybrid, all-wheel drive, advanced driving assistance', 'High-end users with strong eco-awareness', 'Business trips, family travel', 'Luxurious and stable', 'Nappa Leather', 'Plug-in Hybrid'),

-- X7
('BMW021', 'X7 xDrive40Li Luxury Edition Premium Package', 'X7', 'SUV', 103.90, 245, 450, 6.1, NULL, 'Three-row seats, starry panoramic sunroof, crystal electronic gear lever', 'Multi-child families, high-end business users', 'Family travel, business reception', 'Majestic and grand', 'Nappa Leather', 'Petrol'),

-- i Series (Pure Electric)
('BMW022', 'i3 eDrive35L', 'i Series', 'Sedan', 35.39, NULL, 430, 6.2, 520, 'Pure electric drive, rear-wheel drive layout, fast charging function', 'Eco-conscious users, urban commuters', 'Urban driving, daily commuting', 'Minimalist technology', 'Sensatec Synthetic Leather', 'Pure Electric'),
('BMW023', 'i4 eDrive40 Shadow Edition', 'i Series', 'Coupe', 46.99, NULL, 430, 5.7, 590, 'Fastback design, Harman Kardon sound system, fast charging technology', 'Young professionals, environmentalists', 'Urban driving, long-distance travel', 'Sporty technology', 'Sensatec Synthetic Leather', 'Pure Electric'),
('BMW024', 'iX xDrive50 Premium Edition', 'i Series', 'SUV', 99.69, NULL, 630, 4.6, 630, 'Pure electric drive, autonomous driving assistance, crystal interior trim', 'High-end eco-friendly users, technology enthusiasts', 'Long-distance travel, business trips', 'Futuristic', 'Merino Full Leather', 'Pure Electric'),

-- M Series (Performance Cars)
('BMW025', 'M3 Sedan Competition Edition', 'M Series', 'Sedan', 84.99, 375, 650, 3.5, NULL, 'M xDrive all-wheel drive, M carbon ceramic brakes, sports seats', 'Performance enthusiasts, driving fanatics', 'Track experience, mountain road driving', 'Aggressively sporty', 'Merino Full Leather', 'Petrol'),
('BMW026', 'M4 Coupe Competition Edition', 'M Series', '2-Door Coupe', 87.99, 375, 650, 3.5, NULL, 'M compound braking system, active M differential, M sport exhaust', 'Performance enthusiasts, sports car fans', 'Track driving, sports experience', 'Ultimate sporty', 'Merino Full Leather', 'Petrol'),
('BMW027', 'X3 M Competition Edition', 'M Series', 'SUV', 83.99, 353, 600, 4.1, NULL, 'M xDrive all-wheel drive, M sport suspension, performance control system', 'Users seeking both performance and practicality', 'Sports driving, outdoor trips', 'Performance SUV', 'Merino Full Leather', 'Petrol'),

-- Z4
('BMW028', 'Z4 sDrive30i M Sport Package', 'Z4', 'Convertible Sports Car', 53.88, 190, 400, 5.4, NULL, 'Electric soft-top convertible, M Sport package, variable sport steering', 'Sports car enthusiasts, fashionistas', 'Leisure driving, coastal highway driving', 'Classic sporty', 'Sensatec Synthetic Leather', 'Petrol');