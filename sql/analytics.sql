
USE WeatherDataEngineering;
GO

-- 1. Latest weather observation for each city
CREATE OR ALTER VIEW dbo.vw_LatestCityWeather
AS
WITH RankedWeather AS (
    SELECT
        City,
        ObservationTime,
        TemperatureC,
        FeelsLikeC,
        HumidityPercent,
        PrecipitationMM,
        WindSpeedKmh,
        ROW_NUMBER() OVER (
            PARTITION BY City
            ORDER BY ObservationTime DESC
        ) AS rn
    FROM dbo.WeatherObservations
)
SELECT
    City,
    ObservationTime,
    TemperatureC,
    FeelsLikeC,
    HumidityPercent,
    PrecipitationMM,
    WindSpeedKmh
FROM RankedWeather
WHERE rn = 1;
GO

-- 2. Historical summary by city and date
CREATE OR ALTER VIEW dbo.vw_DailyWeatherSummary
AS
SELECT
    CAST(ObservationTime AS DATE) AS ObservationDate,
    City,
    COUNT(*) AS ObservationCount,
    CAST(AVG(TemperatureC) AS DECIMAL(5, 2))
        AS AvgTemperatureC,
    MAX(TemperatureC) AS MaxTemperatureC,
    MAX(FeelsLikeC) AS MaxFeelsLikeC,
    CAST(AVG(HumidityPercent) AS DECIMAL(5, 2))
        AS AvgHumidityPercent
FROM dbo.WeatherObservations
GROUP BY
    CAST(ObservationTime AS DATE),
    City;
GO
