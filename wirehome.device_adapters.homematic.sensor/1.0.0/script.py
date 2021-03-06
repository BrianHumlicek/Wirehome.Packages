SERVICE_ID = "wirehome.services.homematic.ccu"

config = {}


def process_adapter_message(message):
    message_type = message.get("type", None)

    if message_type == "initialize":
        return __initialize__()
    if message_type == "destroy":
        return __destroy__()
    return {
        "type": "exception.not_supported",
        "origin_type": type
    }


def __initialize__():
    result = {"type": "success"}

    global subscription_uid
    subscription_uid = wirehome.context["component_uid"] + "->homematic.ccu.event.device_state_changed"

    address = config.get("address")
    property_name = config.get("property")

    filter = {
        "type": "homematic.ccu.event.device_state_changed",
        "address": address,
        "property": property_name
    }

    wirehome.message_bus.subscribe(subscription_uid, filter, __gateway_manager_callback__)

    initial_value = wirehome.services.invoke(SERVICE_ID, "get_device_value", address, property_name)
    __update_value(initial_value)

    return result


def __destroy__():
    wirehome.message_bus.unsubscribe(subscription_uid)


def __gateway_manager_callback__(message):
    new_state = message.get("new", None)
    __update_value(new_state)


def __update_value(new_state):
    wirehome.publish_adapter_message({
        "type": "value_updated",
        "value": new_state
    })
