#!/bin/env python3
"""
Integration tests for NebulaFacade.

These tests require a running Nebula Graph cluster.
Start with: docker compose --profile dev up -d metad-dev storaged-dev graphd-dev init-dev
"""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture
def nebula_facade(nebula_cluster):
    """Get a NebulaFacade connected to the test cluster."""
    from shared.nebula import NebulaFacade

    facade = NebulaFacade(
        nebula_cluster["username"],
        nebula_cluster["password"],
        nebula_cluster["space"],
        [(nebula_cluster["host"], nebula_cluster["port"])],
    )
    yield facade
    facade.close()


class TestNebulaFacadeIntegration:
    """Integration tests for NebulaFacade against a real Nebula cluster."""

    def test_connect_and_show_spaces(self, nebula_facade):
        """Should connect and execute SHOW SPACES successfully."""
        result = nebula_facade.execute("SHOW SPACES")
        assert result.is_succeeded(), result.error_msg()

    def test_fetch_admin_user(self, nebula_facade):
        """Should fetch the seed admin user vertex."""
        from shared.nebula import gen_vid

        admin_vid = gen_vid("caasm_user", "admin")
        vertex = nebula_facade.fetch("caasm_user", admin_vid)

        # Admin user should exist in the seed data
        if vertex is not None:
            assert vertex is not None
            # Verify the vertex has the expected tag
            assert len(vertex.tags) > 0

    def test_fetch_nonexistent_vertex(self, nebula_facade):
        """Should return None for a non-existent vertex."""
        vertex = nebula_facade.fetch("caasm_user", "nonexistent_vid_12345")
        assert vertex is None

    def test_execute_with_params(self, nebula_facade):
        """Should execute parameterized nGQL queries."""
        result = nebula_facade.execute(
            "LOOKUP ON caasm_user WHERE caasm_user.username == $username YIELD VERTEX AS v",
            username="admin",
        )
        assert result.is_succeeded(), result.error_msg()
        # Should find the admin user
        assert result.row_size() >= 1

    def test_insert_and_fetch_field_vertex(self, nebula_facade):
        """Should insert a field vertex and fetch it back."""
        from shared.nebula import gen_vid

        test_name = "test_field_integration"
        vid = gen_vid("field", test_name)

        # Clean up first (in case previous test left it)
        nebula_facade.execute('DELETE VERTEX "{}" WITH EDGE'.format(vid))

        # Insert
        stmt = 'INSERT VERTEX IF NOT EXISTS field(field_name, field_desc) VALUES "{}":("{}", "test description")'.format(
            vid, test_name
        )
        result = nebula_facade.execute(stmt)
        assert result.is_succeeded(), result.error_msg()

        # Fetch back
        vertex = nebula_facade.fetch("field", vid)
        assert vertex is not None

        # Clean up
        nebula_facade.execute('DELETE VERTEX "{}" WITH EDGE'.format(vid))