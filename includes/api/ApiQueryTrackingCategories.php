<?php
/**
 * Copyright © 2007 Roan Kattouw <roan.kattouw@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 *
 * @file
 */

namespace MediaWiki\Api;

use MediaWiki\Category\TrackingCategories;
use Wikimedia\ParamValidator\ParamValidator;
use Wikimedia\ParamValidator\TypeDef\IntegerDef;
use Wikimedia\Rdbms\IReadableDatabase;

/**
 * Query module to enumerate existing tracking categories. A tracking category exists if it contains pages
 * or if its category page exists.
 *
 * @ingroup API
 */
class ApiQueryTrackingCategories extends ApiQueryCategoryList {
	private TrackingCategories $trackingCategoriesService;

	public function __construct( ApiQuery $query, string $moduleName, TrackingCategories $tc ) {
		parent::__construct( $query, $moduleName, 'tc' );
		$this->trackingCategoriesService = $tc;
	}

	public function execute() {
		$this->run();
	}

	/**
	 * @param array $params
	 * @return string
	 */
	public function getCacheMode( $params ): string {
		return 'public';
	}

	/**
	 * @param ApiPageSet $resultPageSet
	 * @return void
	 */
	public function executeGenerator( $resultPageSet ): void {
		$this->run( $resultPageSet );
	}

	/**
	 * @param ApiPageSet|null $resultPageSet
	 */
	private function run( $resultPageSet = null ) {
		$db = $this->getDB();
		$params = $this->extractRequestParams();

		$this->createQuery( $db, $params );

		$cats = $this->trackingCategoriesService->getTrackingCategories();
		$catNameList = [];
		foreach ( $cats as $id => $cat ) {
			if ( empty( $params['trackingcatname'] ) || in_array( $id, $params['trackingcatname'] ) ) {
				foreach ( $cat['cats'] ?? [] as $link ) {
					$catNameList[ $link->getDbkey() ] = $id;
				}
			}
		}
		if ( $catNameList === [] ) {
			return;
		}
		$this->addWhereFld( 'cat_title', array_keys( $catNameList ) );
		$this->executeQuery( $params, $resultPageSet, [ 'catNames' => $catNameList ] );
	}

	protected function createQuery( IReadableDatabase $db, array $params ): void {
		$params['from'] = null;
		$params['to'] = null;
		$params['prefix'] = null;
		$params['dir'] = 'ascending';
		parent::createQuery( $db, $params );
	}

	public function getAllowedParams(): array {
		return [
			'continue' => [
				ApiBase::PARAM_HELP_MSG => 'api-help-param-continue',
			],
			'trackingcatname' => [
				ParamValidator::PARAM_ISMULTI => true,
			],
			'min' => [
				ParamValidator::PARAM_TYPE => 'integer'
			],
			'max' => [
				ParamValidator::PARAM_TYPE => 'integer'
			],
			'limit' => [
				ParamValidator::PARAM_DEFAULT => 10,
				ParamValidator::PARAM_TYPE => 'limit',
				IntegerDef::PARAM_MIN => 1,
				IntegerDef::PARAM_MAX => ApiBase::LIMIT_BIG1,
				IntegerDef::PARAM_MAX2 => ApiBase::LIMIT_BIG2
			],
			'prop' => [
				ParamValidator::PARAM_TYPE => [ 'size', 'hidden' ],
				ParamValidator::PARAM_DEFAULT => '',
				ParamValidator::PARAM_ISMULTI => true,
				ApiBase::PARAM_HELP_MSG_PER_VALUE => [],
			],
		];
	}

	protected function getExamplesMessages(): array {
		return [
			'action=query&list=trackingcategories&tcprop=size'
				=> 'apihelp-query+trackingcategories-example-size',
			'action=query&generator=trackingcategories&gtctrackingcatname=broken-file-category&prop=info'
				=> 'apihelp-query+trackingcategories-example-generator',
		];
	}

	public function getHelpUrls(): string {
		return 'https://www.mediawiki.org/wiki/Special:MyLanguage/API:Trackingcategories';
	}
}
