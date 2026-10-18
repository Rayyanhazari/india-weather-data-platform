
USE WeatherDataEngineering;
GO

-- 1. Check that all six expected cities exist
WITH ExpectedCities AS (
    SELECT City
    FROM (VALUES
        ('Hyderabad'),
        ('Delhi'),
        ('Mumbai'),
        ('Chennai'),
        ('Bengaluru'),
        ('Kolkata')
    ) AS C(City)
)
SELECT
    E.City AS MissingCity
FROM ExpectedCities E
LEFT JOIN dbo.WeatherObservations W
    ON W.City = E.City
WHERE W.City IS NULL;

-- 2. Check for invalid measurements
SELECT *
FROM dbo.WeatherObservations
WHERE
    HumidityPercent NOT BETWEEN 0 AND 100
    OR PrecipitationMM < 0
    OR WindSpeedKmh < 0;

-- 3. Check for duplicate city/timestamp combinations
SELECT
    City,
    ObservationTime,
    COUNT(*) AS DuplicateCount
FROM dbo.WeatherObservations
GROUP BY City, ObservationTime
HAVING COUNT(*) > 1;

-- 4. Check total observations per city
SELECT
    City,
    COUNT(*) AS TotalObservations,
    MIN(ObservationTime) AS FirstObservation,
    MAX(ObservationTime) AS LastObservation
FROM dbo.WeatherObservations
GROUP BY City
ORDER BY City;
--4.

-- 5. Overall data-quality status
SELECT
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM dbo.WeatherObservations
            WHERE HumidityPercent NOT BETWEEN 0 AND 100
               OR PrecipitationMM < 0
               OR WindSpeedKmh < 0
        )
        THEN 'FAIL'
        WHEN EXISTS (
            SELECT City, ObservationTime
            FROM dbo.WeatherObservations
            GROUP BY City, ObservationTime
            HAVING COUNT(*) > 1
        )
        THEN 'FAIL'
        WHEN (
            SELECT COUNT(DISTINCT City)
            FROM dbo.WeatherObservations
        ) < 6
        THEN 'FAIL'
        ELSE 'PASS'
    END AS DataQualityStatus;
