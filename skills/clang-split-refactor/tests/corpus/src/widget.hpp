#ifndef DEMO_WIDGET_HPP
#define DEMO_WIDGET_HPP
#include <string>
namespace demo {
	std::string run_demo();

	struct Counter {
		int value = 0;
		int next();
	};
}
#endif
