#pragma once


#include "TimeSource.h"
#include "Wm.h"


class GpsTimeSource: public TimeSource, public Wm::Thread {
private:
    ref<Wm::Gps> _gps;


public:
    virtual void finalize() {
        _gps = NULL;
    }


    virtual Wm::String getDescription() {
        return S("Uses the time provided by GPS satellites.");
    }


    virtual Wm::String getName() {
        return S("GPS");
    }


    virtual void initialize() {
        start();
    }


    virtual void run() {
        try {
            _gps = new Wm::Gps();
        }
        catch (Wm::Exception exception) {
            getListener()->onStatusChange(S("Not available: ")
                + exception.getMessage());
            return;
        }

        for (; !_gps.null(); sleep(1 * 1000)) {
            GPS_POSITION position = _gps->getPosition(1 * 1000)->getValue();

            if ((position.dwValidFields & GPS_VALID_UTC_TIME) != 0) {
                getListener()->onTimeChange(position.stUTCTime);
            }
            else {
                getListener()->onStatusChange("No time information available.");
            }
        }
    }
};
