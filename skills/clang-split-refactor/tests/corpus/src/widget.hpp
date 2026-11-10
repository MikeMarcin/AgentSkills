#ifndef DEMO_WIDGET_HPP
#define DEMO_WIDGET_HPP
#include <string>
namespace demo {
	std::string run_demo();

	struct Counter {
		struct Step;
		int value = 0;
		~Counter();
		int next();
	};
}
#endif
