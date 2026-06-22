import logging
from typing import List, Dict, Any, Union, Optional

logger = logging.getLogger(__name__)

class JsonSearchLoader:
    """Parses live flight search JSON results into internally structured itineraries."""

    def _extract_raw_flights(self, json_data: Union[List[Any], Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Safely extracts flights whether the JSON root is a list or a dictionary."""
        try:
            if isinstance(json_data, list):
                logger.info(f"Detected JSON root type: List. Total potential itineraries loaded: {len(json_data)}")
                return json_data
            
            if isinstance(json_data, dict):
                # dynamically detect arrays
                for key, value in json_data.items():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        logger.info(f"Detected JSON root type: Dict. Extracted array from key '{key}' with {len(value)} potential itineraries.")
                        return value
                
            logger.warning(f"Unexpected JSON root type: {type(json_data)}. Returning empty list.")
            return []
        except Exception as e:
            logger.exception("Failed to extract raw flights from JSON data.")
            return []

    def load_oneway(self, json_data: Union[List[Any], Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self._extract_raw_flights(json_data)
        
    def load_roundtrip(self, json_data: Union[List[Any], Dict[str, Any]]) -> List[Dict[str, Any]]:
        return self._extract_raw_flights(json_data)
        
    def _extract_origin(self, legs: List[Dict[str, Any]]) -> str:
        if not legs or not isinstance(legs, list) or not isinstance(legs[0], dict): return ""
        return str(legs[0].get("origin_code") or legs[0].get("origin", "")).strip().upper()

    def _extract_destination(self, legs: List[Dict[str, Any]]) -> str:
        if not legs or not isinstance(legs, list) or not isinstance(legs[0], dict): return ""
        return str(legs[0].get("destination_code") or legs[0].get("destination", "")).strip().upper()

    def _extract_departure_time(self, legs: List[Dict[str, Any]]) -> str:
        if not legs or not isinstance(legs, list) or not isinstance(legs[0], dict): return ""
        return str(legs[0].get("departure_time", "")).strip()

    def _extract_arrival_time(self, legs: List[Dict[str, Any]]) -> str:
        if not legs or not isinstance(legs, list) or not isinstance(legs[-1], dict): return ""
        return str(legs[-1].get("arrival_time", "")).strip()

    def _extract_duration(self, legs: List[Dict[str, Any]]) -> int:
        if not isinstance(legs, list): return 0
        return sum(int(leg.get("duration_minutes", 0)) for leg in legs if isinstance(leg, dict))

    def _extract_stop_count(self, legs: List[Dict[str, Any]]) -> int:
        if not isinstance(legs, list): return 0
        return sum(int(leg.get("stops", leg.get("stop_count", 0))) for leg in legs if isinstance(leg, dict))

    def _extract_supplier(self, f: Dict[str, Any]) -> str:
        return str(f.get("source") or f.get("supplier_code") or f.get("supplier", "")).strip()

    def _extract_airline(self, f: Dict[str, Any]) -> str:
        return str(f.get("plating_carrier") or f.get("airline_code") or f.get("airline", "")).strip()

    def _extract_price(self, fares: List[Dict[str, Any]]) -> float:
        if not fares or not isinstance(fares, list) or not isinstance(fares[0], dict): return 0.0
        fare = fares[0]
        price_obj = fare.get("price", {})
        if isinstance(price_obj, dict):
            return float(price_obj.get("total") or price_obj.get("amount", 0.0))
        return float(price_obj or 0.0)

    def _extract_baggage(self, fares: List[Dict[str, Any]]) -> str:
        if not fares or not isinstance(fares, list) or not isinstance(fares[0], dict): return "0KG"
        return str(fares[0].get("baggage", "0KG")).strip()

    def _extract_refundability(self, fares: List[Dict[str, Any]]) -> bool:
        if not fares or not isinstance(fares, list) or not isinstance(fares[0], dict): return False
        return bool(fares[0].get("is_refundable") or fares[0].get("refundable", False))

    def _extract_meals(self, fares: List[Dict[str, Any]]) -> bool:
        if not fares or not isinstance(fares, list) or not isinstance(fares[0], dict): return False
        return bool(fares[0].get("meals", False))
        
    def _extract_departure_hour(self, dep_time: str) -> int:
        if dep_time and isinstance(dep_time, str) and "T" in dep_time:
            try:
                time_part = dep_time.split("T")[1]
                return int(time_part.split(":")[0])
            except Exception:
                pass
        return 12

    def _extract_flight_numbers(self, legs: List[Dict[str, Any]]) -> List[str]:
        flight_numbers = []
        if isinstance(legs, list):
            for leg in legs:
                if isinstance(leg, dict):
                    segments = leg.get("segments", [])
                    if isinstance(segments, list):
                        for seg in segments:
                            if isinstance(seg, dict):
                                al = seg.get("airline_code") or seg.get("operating_airline_code", "")
                                fn = seg.get("flight_number", "")
                                if al and fn:
                                    flight_numbers.append(f"{al}{fn}")
        return flight_numbers or ["UNK123"]

    def _extract_all_segments(self, itinerary: Dict[str, Any]) -> List[Dict[str, Any]]:
        segments = itinerary.get("segments", [])
        if not segments:
            segments = (
                itinerary.get("journeys", [])
                or itinerary.get("slices", [])
                or itinerary.get("legs", [])
                or itinerary.get("itineraries", [])
                or itinerary.get("offers", [])
                or itinerary.get("trips", [])
                or []
            )
            
        extracted = []
        for seg in segments:
            if isinstance(seg, dict):
                o = seg.get("origin_code") or seg.get("origin")
                d = seg.get("destination_code") or seg.get("destination")
                
                # Step 6: Support Route Extraction from Nested Segments
                nested = seg.get("segments", [])
                if not nested:
                    nested = seg.get("legs", []) or seg.get("slices", [])
                    
                if not o and nested and isinstance(nested, list) and len(nested) > 0:
                    o = nested[0].get("origin_code") or nested[0].get("origin")
                if not d and nested and isinstance(nested, list) and len(nested) > 0:
                    d = nested[-1].get("destination_code") or nested[-1].get("destination")
                    
                if o and d:
                    seg_copy = seg.copy()
                    seg_copy["origin"] = o
                    seg_copy["destination"] = d
                    extracted.append(seg_copy)
                else:
                    extracted.extend(self._extract_all_segments(seg))
                    
        if not extracted and isinstance(itinerary, dict):
            o = itinerary.get("origin_code") or itinerary.get("origin")
            d = itinerary.get("destination_code") or itinerary.get("destination")
            if o and d:
                extracted.append(itinerary)
                
        return extracted

    def normalize_itineraries(self, raw_flights: List[Dict[str, Any]], origin: str, destination: str, trip_type: str = "oneway") -> List[Dict[str, Any]]:
        """Filters, validates, and normalizes the parsed itineraries to guarantee consistency."""
        normalized = []
        suppliers_seen = set()
        
        target_origin = str(origin).strip().upper()
        target_dest = str(destination).strip().upper()
        trip_type = trip_type.lower()
        
        raw_records = len(raw_flights)
        segment_matches = 0
        paired_roundtrips = 0
        normalized_count = 0
        failed_count = 0
        
        for f in raw_flights:
            if not isinstance(f, dict):
                failed_count += 1
                continue
                
            supplier_code = self._extract_supplier(f)
            fares = f.get("fares", [f])
            if not isinstance(fares, list) or not fares:
                fares = [f]
                
            price = self._extract_price(fares)
            airline = self._extract_airline(f)
            
            # Step 1: Recursive extraction
            extracted_segments = self._extract_all_segments(f)
            if not extracted_segments:
                failed_count += 1
                continue
                
            # Step 5: Relaxed validation
            if not supplier_code and not price and not extracted_segments:
                failed_count += 1
                continue
                
            # Step 2: Segment-level matching
            outbound_segments = []
            inbound_segments = []
            
            for seg in extracted_segments:
                s_orig = str(seg.get("origin", "")).strip().upper()
                s_dest = str(seg.get("destination", "")).strip().upper()
                
                if s_orig == target_origin and s_dest == target_dest:
                    outbound_segments.append(seg)
                elif s_orig == target_dest and s_dest == target_origin:
                    inbound_segments.append(seg)
                    
            if not outbound_segments and not inbound_segments:
                logger.warning(f"No segments matched route {target_origin}->{target_dest} for supplier {supplier_code}")
                failed_count += 1
                continue
                
            segment_matches += (len(outbound_segments) + len(inbound_segments))
            
            combined = []
            
            # Step 3: Combination generation
            if trip_type == "roundtrip":
                for outbound in outbound_segments:
                    for inbound in inbound_segments:
                        out_dep = str(outbound.get("departure_time", ""))
                        in_dep = str(inbound.get("departure_time", ""))
                        
                        if in_dep and out_dep and in_dep <= out_dep:
                            continue
                            
                        combined.append({
                            "supplier_code": supplier_code or self._extract_supplier(outbound),
                            "airline": airline or self._extract_airline(outbound),
                            "outbound": outbound,
                            "inbound": inbound
                        })
                paired_roundtrips += len(combined)
            else:
                for outbound in outbound_segments:
                    combined.append({
                        "supplier_code": supplier_code or self._extract_supplier(outbound),
                        "airline": airline or self._extract_airline(outbound),
                        "outbound": outbound,
                        "inbound": None
                    })
                    
            if not combined:
                failed_count += 1
                continue
                
            # Step 4: Normalizer combination
            for combo in combined:
                try:
                    outbound = combo["outbound"]
                    inbound = combo["inbound"]
                    
                    currency_val = "EUR"
                    if fares and isinstance(fares, list) and isinstance(fares[0], dict):
                        price_dict = fares[0].get("price", {})
                        if isinstance(price_dict, dict):
                            currency_val = str(f.get("currency") or price_dict.get("currency") or "EUR")
                    
                    total_duration = int(outbound.get("duration_minutes", 0))
                    total_stops = int(outbound.get("stops", outbound.get("stop_count", 0)))
                    dep_time = str(outbound.get("departure_time", ""))
                    flight_numbers = self._extract_flight_numbers([outbound])
                    
                    if inbound:
                        total_duration += int(inbound.get("duration_minutes", 0))
                        total_stops += int(inbound.get("stops", inbound.get("stop_count", 0)))
                        flight_numbers.extend(self._extract_flight_numbers([inbound]))
                        
                    norm_flight = {
                        "supplier_code": str(combo["supplier_code"]),
                        "airline": str(combo["airline"]),
                        "origin": target_origin,
                        "destination": target_dest,
                        "price": float(price or 0.0),
                        "duration_minutes": total_duration,
                        "stops": total_stops,
                        "refundable": bool(self._extract_refundability(fares)),
                        "baggage": str(self._extract_baggage(fares) or "N/A"),
                        "meals": bool(self._extract_meals(fares)),
                        "departure_hour": int(self._extract_departure_hour(dep_time) or 0),
                        "currency": currency_val,
                        "flight_numbers": flight_numbers,
                        "cabin": str(f.get("cabin") or f.get("cabin_class", "Economy")),
                        "trip_type": trip_type
                    }
                    
                    normalized.append(norm_flight)
                    suppliers_seen.add(norm_flight["supplier_code"])
                    normalized_count += 1
                except Exception as e:
                    logger.warning(f"Error combining segments: {str(e)}")
                    failed_count += 1

        # Step 7: Enterprise Diagnostics
        logger.info({
            "raw_records": raw_records,
            "segment_matches": segment_matches,
            "paired_roundtrips": paired_roundtrips,
            "normalized_count": normalized_count,
            "failed_count": failed_count
        })
        
        return normalized
