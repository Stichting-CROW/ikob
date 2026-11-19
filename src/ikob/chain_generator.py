import logging
from pathlib import Path

import numpy as np
import numpy.typing as npt

from ikob import utils
from ikob.id_store import ZoneIdStoreSingleton
from ikob.utils import FLOAT_DTYPE, IKOB_INFINITE

logger = logging.getLogger(__name__)


class Hubs:
    def __init__(
        self,
        zone_indices: list[int],
        hub_costs_cents: npt.NDArray[FLOAT_DTYPE],
        pt_transfer_times: npt.NDArray[FLOAT_DTYPE],
        bike_transfer_times: npt.NDArray[FLOAT_DTYPE],
        pay_for_pt: npt.NDArray[np.bool_],
        num_hubs: int,
    ):
        self.zone_indices = zone_indices
        self.hub_costs_cents = hub_costs_cents
        self.pt_transfer_times = pt_transfer_times
        self.bike_transfer_times = bike_transfer_times
        self.pay_for_pt = pay_for_pt
        self.num_hubs = num_hubs

    @classmethod
    def build_from_config(cls, config):
        """Build a Hubs object from the config"""

        hub_raw = cls._read_hubs_from_file(config)

        zone_id_store = ZoneIdStoreSingleton.get_instance(config)

        zone_indices: list[int] = [zone_id_store._id_to_idx[zone_id] for zone_id in hub_raw[:, 0]]
        hub_costs_cents: npt.NDArray[FLOAT_DTYPE] = hub_raw[:, 1].astype(FLOAT_DTYPE)
        pt_transfer_times: npt.NDArray[FLOAT_DTYPE] = hub_raw[:, 2].astype(FLOAT_DTYPE)
        bike_transfer_times: npt.NDArray[FLOAT_DTYPE] = hub_raw[:, 3].astype(FLOAT_DTYPE)
        pay_for_pt: npt.NDArray[np.bool_] = hub_raw[:, 4].astype(int).astype(bool)
        num_hubs: int = len(hub_raw)

        return cls(
            zone_indices,
            hub_costs_cents,
            pt_transfer_times,
            bike_transfer_times,
            pay_for_pt,
            num_hubs,
        )

    @staticmethod
    def validate(config):
        valid = True
        use_chains = config["ketens"]["chains"]["gebruiken"]
        use_destination_list = config["ketens"]["bestemmingslijst"]["gebruiken"]

        if use_chains:
            valid &= Hubs._validate_hubs_file(config)

        if use_destination_list:
            valid &= Hubs._validate_destinations_file(config)
            if not use_chains:
                logger.warning(
                    "Usage of a hub destination list is set to true in the config, but the usage of hubs itself is set to false. "
                )

        return valid

    @staticmethod
    def _validate_hubs_file(config):
        hub_content_raw = Hubs._read_hubs_from_file(config)

        if hub_content_raw.shape[0] == 0:
            logger.warning("Hub data is empty.")
            return False

        if hub_content_raw.shape[1] != 5:
            logger.warning(f"Hub data should have 5 columns but has {hub_content_raw.shape[1]}.")
            return False

        valid = True
        try:
            hub_content_raw[:, 1:4].astype(FLOAT_DTYPE)
        except ValueError:
            logger.warning(
                "Columns 2-4 of the hub data (in order: price of hub, PT transfer time, bike transfer time) should contain numbers."
            )
            valid = False
        try:
            # We must first convert to int bc the string 0 gets cast to True
            pay_for_pt_int = hub_content_raw[:, 4].astype(int)
            if (pay_for_pt_int < 0).any() or (pay_for_pt_int > 1).any():
                logger.warning("The fifth column of the hub data (whether to pay for pt) should contain either 0 or 1.")
                valid = False
        except ValueError:
            logger.warning("The fifth column of the hub data (whether to pay for pt) should contain either 0 or 1.")
            valid = False

        return valid

    @staticmethod
    def _validate_destinations_file(config):
        destination_list_path = Path(config["ketens"]["bestemmingslijst"]["bestand"])
        # Reading the full file implicitly asserts that the header row and data row have the same number of entries
        try:
            destination_file_full = np.loadtxt(destination_list_path, dtype=str, skiprows=0, delimiter=",", ndmin=2)
        except Exception as e:
            logger.warning("An exception occurred while reading the destination file", exc_info=e)
            return False

        if len(destination_file_full) != 2:
            logger.warning("Destinations file should contain two rows. One header row and one row of zone id's.")
            return False

        # Try to read the file using its standard interface to check for any zone mapping issues
        try:
            Hubs.read_destinations_from_file(config)
        except Exception as e:
            logger.warning("An exception occurred while loading the destination file", exc_info=e)
            return False

        return True

    @staticmethod
    def read_destinations_from_file(config) -> npt.NDArray:
        destination_list_path = Path(config["ketens"]["bestemmingslijst"]["bestand"])
        destination_list_id = np.loadtxt(destination_list_path, dtype=str, skiprows=1, delimiter=",", ndmin=1)

        zone_id_store = ZoneIdStoreSingleton.get_instance(config)

        destination_list_idx = np.asarray(
            [zone_id_store._id_to_idx[destination_id] for destination_id in destination_list_id]
        ).astype(int)

        return destination_list_idx

    @staticmethod
    def _read_hubs_from_file(config):
        hubs_path = Path(config["ketens"]["chains"]["bestand"])
        return np.loadtxt(hubs_path, dtype=str, skiprows=1, delimiter=",", ndmin=2)


class ChainTravelTimeCalculator:
    """Compute chain matrices for one set of skim matrices at a time."""

    def __init__(self, hubs: Hubs, additional_costs: npt.NDArray, parking_times: npt.NDArray, destination_list):
        self.hubs = hubs
        self.additional_costs = additional_costs
        self.parking_times = parking_times
        self.destination_list = destination_list

    def compute(
        self,
        car_time: npt.NDArray,
        car_dist: npt.NDArray,
        bike_time: npt.NDArray,
        bike_dist: npt.NDArray,
        pt_time: npt.NDArray,
        pt_cost: npt.NDArray,
        tvom_factor: float,
        var_car_rate: float,
        road_pricing: float,
        bike_cost_euro_per_km: float,
    ) -> tuple[npt.NDArray, npt.NDArray]:
        return compute_chain_travel_time(
            hubs=self.hubs,
            car_time=car_time,
            car_dist=car_dist,
            bike_time=bike_time,
            bike_dist=bike_dist,
            pt_time=pt_time,
            pt_cost=pt_cost,
            tvom_factor=tvom_factor,
            var_car_rate=var_car_rate,
            road_pricing=road_pricing,
            bike_cost_euro_per_km=bike_cost_euro_per_km,
            additional_costs=self.additional_costs,
            parking_times=self.parking_times,
            destination_list=self.destination_list,
        )


def build_chain_travel_time_calculator(config, parking_times, additional_costs) -> ChainTravelTimeCalculator:
    hubs = Hubs.build_from_config(config)
    if hubs.num_hubs == 0:
        logger.warning("Chain generator called but no hubs found in file at config['ketens']['chains'].")

    zone_id_store = ZoneIdStoreSingleton.get_instance(config)
    if config["ketens"]["bestemmingslijst"]["gebruiken"]:
        destination_list = Hubs.read_destinations_from_file(config)
    else:
        destination_list = np.arange(zone_id_store._num_zones)

    return ChainTravelTimeCalculator(
        hubs=hubs,
        additional_costs=additional_costs,
        parking_times=np.asarray(parking_times, dtype=utils.FLOAT_DTYPE),
        destination_list=destination_list,
    )


def compute_chain_travel_time(
    hubs: Hubs,
    car_time: npt.NDArray,
    car_dist: npt.NDArray,
    bike_time: npt.NDArray,
    bike_dist: npt.NDArray,
    pt_time: npt.NDArray,
    pt_cost: npt.NDArray,
    tvom_factor: float,
    var_car_rate: float,
    road_pricing: float,
    bike_cost_euro_per_km: float,
    additional_costs: npt.NDArray,
    parking_times: npt.NDArray,
    destination_list: npt.NDArray[np.integer],
) -> tuple[npt.NDArray, npt.NDArray]:
    """Compute Park+Bike and Park+Ride generalized travel time skims.

    For each hub, vectorized over all origin-destination pairs. Returns the
    element-wise minimum across all hubs.
    """
    num_zones = len(car_time)

    # Only compute chain travel times for zones in the destination_list.
    # This allows a user to investigate hub locations to improve travel times to only a subset of the total zones.
    destination_mask = np.zeros(num_zones, dtype=bool)
    destination_mask[destination_list] = True

    # Initialize with true infinite values to overwrite these with gtt even if those are above IKOB_INFINITE
    result_bike = np.full((num_zones, num_zones), np.inf, dtype=utils.FLOAT_DTYPE)
    result_ride = np.full((num_zones, num_zones), np.inf, dtype=utils.FLOAT_DTYPE)

    # Hubs have their own transfer time that includes the parking time
    hub_parking_times = parking_times.copy()
    hub_parking_times[:, 1] = 0.0

    if hubs.num_hubs == 0:
        result_bike = np.where(result_bike == np.inf, IKOB_INFINITE, result_bike)
        result_ride = np.where(result_ride == np.inf, IKOB_INFINITE, result_ride)
        return result_bike, result_ride

    hub_zones = hubs.zone_indices
    hub_costs = hubs.hub_costs_cents / 100
    change_time_bike = hubs.bike_transfer_times
    change_time_pt = hubs.pt_transfer_times
    pay_for_pt = hubs.pay_for_pt

    # Travel via a hub consist of going by car to the hub, then continuing either by bike or by pt
    car_part = (
        utils.compute_car_gtt(
            car_time=car_time,
            car_dist=car_dist,
            var_rate=var_car_rate,
            road_pricing=road_pricing,
            tvom_factor=tvom_factor,
            additional_costs_eurocent=additional_costs,
            parking_costs_array_eurocent=np.zeros(
                num_zones, dtype=utils.FLOAT_DTYPE
            ),  # parking costs are in the hub_cost
            parking_times_array=hub_parking_times,
        )[:, hub_zones]
        + hub_costs[np.newaxis, :] * tvom_factor
    )
    bike_part = utils.compute_bike_gtt(bike_time, bike_dist, bike_cost_euro_per_km, tvom_factor)[hub_zones, :]
    pt_part = utils.compute_pt_gtt(
        pt_time[hub_zones, :], pt_cost[hub_zones, :] * pay_for_pt[:, np.newaxis], tvom_factor
    )

    # Car from origin to hub, then some change time at the hub, then bike / pt from hub destination
    # Loop over hubs to avoid having to hold a 3D array in memory
    for hub_idx in range(car_part.shape[1]):
        via_hub = (
            car_part[:, hub_idx][:, np.newaxis]
            + change_time_bike[hub_idx]
            + bike_part[hub_idx, :][np.newaxis, destination_mask]
        )
        result_bike[:, destination_mask] = np.minimum(result_bike[:, destination_mask], via_hub)

    for hub_idx in range(car_part.shape[1]):
        via_hub = (
            car_part[:, hub_idx][:, np.newaxis]
            + change_time_pt[hub_idx]
            + pt_part[hub_idx, :][np.newaxis, destination_mask]
        )
        result_ride[:, destination_mask] = np.minimum(result_ride[:, destination_mask], via_hub)

    result_bike = np.where(result_bike == np.inf, IKOB_INFINITE, result_bike)
    result_ride = np.where(result_ride == np.inf, IKOB_INFINITE, result_ride)
    return result_bike, result_ride
