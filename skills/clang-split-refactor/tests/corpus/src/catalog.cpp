#include <string>

namespace demo {
	namespace {
		// Every class and its out-of-line members sit in one anonymous namespace.
		class Catalog {
		public:
			int size() const;
			int twice() const;
		};

		int Catalog::size() const {
			return 2;
		}

		int Catalog::twice() const {
			return size() * 2;
		}
	}

	int catalog_size() {
		return Catalog{}.twice();
	}
}
